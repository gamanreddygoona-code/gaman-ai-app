"""
local_llm.py
────────────
Fast local LLM engine using llama-cpp-python + GGUF models.
10-100x faster than GPT-J-6B via transformers on CPU.

Supported models (auto-detected in ./models/):
  - Phi-3.5-mini-instruct  (2.3 GB, Microsoft, very smart)
  - Qwen2.5-3B-Instruct    (1.9 GB, Alibaba, excellent coder)
  - Llama-3.2-3B-Instruct  (1.8 GB, Meta, fast & capable)

Download a model:
  python local_llm.py --download 0
Test it:
  python local_llm.py --test
"""

import os
import threading
from pathlib import Path

MODELS_DIR = Path("./models")
MODELS_DIR.mkdir(exist_ok=True)

MODEL_OPTIONS = [
    {
        "name": "CodeLlama-7B-Instruct",
        "filename": "codellama-7b-instruct.Q4_K_M.gguf",
        "repo": "TheBloke/CodeLlama-7B-Instruct-GGUF",
        "size": "4.3GB",
        "type": "code",
        "speed": "⚡ Very Fast",
        "reasoning": "Good (for coding)",
    },
    {
        "name": "Mistral-7B-Instruct-v0.3",
        "filename": "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "repo": "bartowski/Mistral-7B-Instruct-v0.3-GGUF",
        "size": "4.4GB",
        "type": "general",
        "speed": "⚡ Very Fast",
        "reasoning": "⭐⭐⭐⭐⭐ Best 7B — BEATS GPT-3.5 on reasoning",
    },
    {
        "name": "Phi-3.5-mini-instruct",
        "filename": "Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "repo": "bartowski/Phi-3.5-mini-instruct-GGUF",
        "size": "2.3GB",
        "type": "general",
        "speed": "⚡⚡ Fastest",
        "reasoning": "⭐⭐⭐⭐ Excellent for size — matches 7B on many tasks",
    },
    {
        "name": "Qwen2.5-7B-Instruct",
        "filename": "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        "repo": "bartowski/Qwen2.5-7B-Instruct-GGUF",
        "size": "4.7GB",
        "type": "general",
        "speed": "⚡ Very Fast",
        "reasoning": "⭐⭐⭐⭐⭐ Top 7B — excellent coding AND reasoning",
    },
    {
        "name": "Orca-2-7B",
        "filename": "orca-2-7b.Q4_K_M.gguf",
        "repo": "TheBloke/Orca-2-7B-GGUF",
        "size": "4.6GB",
        "type": "reasoning",
        "speed": "⚡ Very Fast",
        "reasoning": "⭐⭐⭐⭐⭐ BEATS GPT-3.5",
    },
    {
        "name": "Llama-2-7B-Chat",
        "filename": "llama-2-7b-chat.Q4_K_M.gguf",
        "repo": "TheBloke/Llama-2-7B-Chat-GGUF",
        "size": "4.0GB",
        "type": "chat",
        "speed": "⚡ Very Fast",
        "reasoning": "⭐⭐⭐ Good all-around",
    },
]

_llm = None
_lock = threading.Lock()
_model_loaded = False
_model_name = "None"

SYSTEM_PROMPT = """You are Gaman AI — a brilliant, fast, and highly capable local AI assistant.
You reason step-by-step, write complete runnable code, and give direct expert answers.
You never say 'I cannot help' or 'use ChatGPT instead'. You always try your best.
For code questions: write complete, working code with brief explanations.
For concept questions: explain clearly with examples.
Be concise but thorough. No filler phrases."""


def _find_existing_model() -> str | None:
    """Find the best available GGUF model in ./models/ (prefer Mistral > Qwen > CodeLlama)."""
    # Preferred order: Mistral first (best reasoning), then others
    preferred_order = [
        "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        "Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "orca-2-7b.Q4_K_M.gguf",
        "llama-2-7b-chat.Q4_K_M.gguf",
        "codellama-7b-instruct.Q4_K_M.gguf",
    ]
    for filename in preferred_order:
        path = MODELS_DIR / filename
        if path.exists():
            return str(path)
    # Fallback to any GGUF file
    gguf_files = list(MODELS_DIR.glob("*.gguf"))
    if gguf_files:
        return str(sorted(gguf_files, key=lambda x: x.stat().st_size, reverse=True)[0])
    return None


def download_model(model_idx: int = 0) -> str | None:
    """Download a GGUF model from HuggingFace Hub."""
    try:
        from huggingface_hub import hf_hub_download
        opt = MODEL_OPTIONS[model_idx]
        print(f"[local_llm] Downloading {opt['name']} ({opt['size']}) ...")
        path = hf_hub_download(
            repo_id=opt["repo"],
            filename=opt["filename"],
            local_dir=str(MODELS_DIR),
        )
        print(f"[local_llm] Saved to: {path}")
        return path
    except Exception as e:
        print(f"[local_llm] Download failed: {e}")
        print("[local_llm] Install huggingface_hub: pip install huggingface_hub")
        return None


def _load_via_llama_cpp(model_path: str) -> bool:
    """Try loading via llama-cpp-python (preferred)."""
    global _llm, _model_loaded, _model_name
    try:
        from llama_cpp import Llama
        import multiprocessing
        n_threads = min(multiprocessing.cpu_count(), 8)
        _model_name = Path(model_path).name
        print(f"[local_llm] Loading {_model_name} via llama-cpp ({n_threads} threads) ...")
        _llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=n_threads,
            n_gpu_layers=0,
            verbose=False,
            chat_format="chatml",
        )
        _model_loaded = True
        print(f"[local_llm] ✅ Ready: {_model_name} (llama-cpp)")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"[local_llm] llama-cpp load failed: {e}")
        return False


def _load_via_ctransformers(model_path: str) -> bool:
    """Fallback: load via ctransformers."""
    global _llm, _model_loaded, _model_name
    try:
        from ctransformers import AutoModelForCausalLM
        _model_name = Path(model_path).name
        model_type = "mistral" if "mistral" in _model_name.lower() else \
                     "llama" if "llama" in _model_name.lower() else \
                     "gpt2"
        print(f"[local_llm] Loading {_model_name} via ctransformers ({model_type})...")
        _llm = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type=model_type,
            max_new_tokens=512,
            context_length=2048,
        )
        _llm._backend = "ctransformers"
        _model_loaded = True
        print(f"[local_llm] ✅ Ready: {_model_name} (ctransformers)")
        return True
    except ImportError:
        print("[local_llm] ctransformers not installed. Run: pip install ctransformers")
        return False
    except Exception as e:
        print(f"[local_llm] ctransformers load failed: {e}")
        return False


def load_model() -> bool:
    """Load the GGUF model (singleton, thread-safe). Tries llama-cpp then ctransformers."""
    global _llm, _model_loaded, _model_name
    if _model_loaded:
        return True

    with _lock:
        if _model_loaded:
            return True

        model_path = _find_existing_model()
        if not model_path:
            print("[local_llm] No GGUF model found in ./models/")
            print("[local_llm] Run: python local_llm.py --download 1  (downloads Mistral-7B)")
            return False

        # Try llama-cpp-python first (faster, better), fall back to ctransformers
        if _load_via_llama_cpp(model_path):
            return True
        if _load_via_ctransformers(model_path):
            return True

        print("[local_llm] Could not load model. Install: pip install llama-cpp-python")
        print("[local_llm]   or: pip install ctransformers")
        return False


def generate(
    user_msg: str,
    history: list[dict] | None = None,
    system: str | None = None,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Generate a response using the local GGUF model (llama-cpp or ctransformers)."""
    if not load_model():
        return ""

    if system is None:
        system = SYSTEM_PROMPT

    # ctransformers backend: format as Mistral instruction string
    if hasattr(_llm, "_backend") and _llm._backend == "ctransformers":
        try:
            hist_text = ""
            for turn in (history or [])[-4:]:
                hist_text += f"[INST] {turn.get('user','')} [/INST] {turn.get('bot','')} "
            prompt = f"[INST] {system}\n\n{hist_text}{user_msg} [/INST]"
            return _llm(prompt)[:max_tokens]
        except Exception as e:
            print(f"[local_llm] ctransformers generation error: {e}")
            return ""

    # llama-cpp backend: use chat completion API
    messages = [{"role": "system", "content": system}]
    for turn in (history or [])[-6:]:
        messages.append({"role": "user", "content": turn.get("user", "")})
        messages.append({"role": "assistant", "content": turn.get("bot", "")})
    messages.append({"role": "user", "content": user_msg})

    try:
        output = _llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95,
            stop=["<|user|>", "<|end|>", "User:"],
        )
        return output["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[local_llm] Generation error: {e}")
        return ""


def generate_stream(
    user_msg: str,
    history: list[dict] | None = None,
    system: str | None = None,
    max_tokens: int = 512,
    temperature: float = 0.7,
):
    """Yield tokens one-by-one for streaming responses."""
    if not load_model():
        yield "Model not loaded. Run: python local_llm.py --download 0"
        return

    if system is None:
        system = SYSTEM_PROMPT

    messages = [{"role": "system", "content": system}]
    for turn in (history or [])[-6:]:
        messages.append({"role": "user", "content": turn.get("user", "")})
        messages.append({"role": "assistant", "content": turn.get("bot", "")})
    messages.append({"role": "user", "content": user_msg})

    try:
        for chunk in _llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95,
            stop=["<|user|>", "<|end|>", "User:"],
            stream=True,
        ):
            delta = chunk["choices"][0].get("delta", {})
            token = delta.get("content", "")
            if token:
                yield token
    except Exception as e:
        print(f"[local_llm] Stream error: {e}")


def is_available() -> bool:
    return _model_loaded or bool(_find_existing_model())


def get_model_name() -> str:
    return _model_name


if __name__ == "__main__":
    import sys

    if "--download" in sys.argv:
        idx = 0
        try:
            idx = int(sys.argv[sys.argv.index("--download") + 1])
        except (IndexError, ValueError):
            pass
        download_model(idx)

    elif "--test" in sys.argv:
        if load_model():
            print("Testing generation...")
            resp = generate("Write a Python function to reverse a string.")
            print(f"\nResponse:\n{resp}")
        else:
            print("Model not loaded.")

    else:
        print("Usage: python local_llm.py --download [0|1|2] | --test")
        print("\nAvailable models:")
        for i, opt in enumerate(MODEL_OPTIONS):
            path = MODELS_DIR / opt["filename"]
            status = "✅ Ready" if path.exists() else "⬇  Not downloaded"
            print(f"  {i}. {opt['name']} ({opt['size']}) — {status}")
