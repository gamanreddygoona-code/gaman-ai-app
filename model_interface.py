"""model_interface.py

CPU-friendly wrapper for loading an LLM and generating text.

- Attempts 4-bit quantized loading via `bitsandbytes` (BitsAndBytesConfig).
- Falls back to fp16 loading if bitsandbytes is not available.
- Provides a `generate` function compatible with the existing code base.
- Includes a small CLI test block.
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Optional import for 4-bit quantisation
try:
    from transformers import BitsAndBytesConfig
    _HAS_BITSANDBYTES = True
except Exception:
    _HAS_BITSANDBYTES = False

# Global singleton instances
_MODEL = None
_TOKENIZER = None

def _load_model():
    """Load the model (singleton) with CPU-friendly configuration.

    The model name is taken from the `GAMAN_MODEL_NAME` environment variable;
    defaults to a modest 6B model that fits on most machines.
    """
    global _MODEL, _TOKENIZER
    if _MODEL is not None:
        return
    model_name = os.getenv("GAMAN_MODEL_NAME", "EleutherAI/gpt-j-6b")
    
    global _HAS_BITSANDBYTES
    if _HAS_BITSANDBYTES:
        try:
            bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
            print(f"[model_interface] Loading {model_name} with 4-bit quantisation.")
            _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
            _MODEL = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                quantization_config=bnb_cfg,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
            )
        except Exception as e:
            print(f"[model_interface] 4-bit load failed ({e}), falling back to fp16.")
            _HAS_BITSANDBYTES = False
            
    if not _HAS_BITSANDBYTES:
        # fp16 fallback - still CPU-only but more memory-heavy.
        print(f"[model_interface] Loading {model_name} in fp16 (CPU).")
        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        _MODEL = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        )
    _MODEL.eval()
    print("[model_interface] Model loaded successfully.")

def generate(
    prompt: str,
    max_new_tokens: int = 512,
    temperature: float = 0.8,
    top_p: float = 0.95,
    stop: str | None = None,
    user_message: str | None = None,
    _skip_local_llm: bool = False,
) -> str:
    """Generate a continuation for *prompt*.

    Parameters mirror the OpenAI completion API for easy downstream use.
    The `user_message` parameter is accepted for backward compatibility.
    """
    if not prompt:
        return ""

    # Prefer fast local GGUF model (llama-cpp-python) over heavy GPT-J-6B
    if not _skip_local_llm:
        try:
            import local_llm
            if local_llm.is_available():
                msg = user_message or prompt
                result = local_llm.generate(msg, max_tokens=max_new_tokens, temperature=temperature)
                if result:
                    return result
        except Exception as e:
            print(f"[model_interface] local_llm failed ({e}), falling back to GPT-J")

    _load_model()
    inputs = _TOKENIZER(prompt, return_tensors="pt")
    inputs = {k: v.to(_MODEL.device) for k, v in inputs.items()}
    with torch.no_grad():
        output = _MODEL.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=_TOKENIZER.eos_token_id,
        )
    text = _TOKENIZER.decode(output[0], skip_special_tokens=True)
    # Strip the original prompt from the beginning of the response.
    if text.startswith(prompt):
        text = text[len(prompt) :]
    if stop and stop in text:
        text = text.split(stop)[0]
    return text.strip()

def list_available_models() -> list:
    """Return a small curated list of CPU-friendly model identifiers."""
    return [
        "EleutherAI/gpt-j-6b",
        "facebook/opt-6.7b",
        "meta-llama/Llama-2-7b-chat-hf",
        "TencentARC/GPT-OSS-120B",
    ]

if __name__ == "__main__":
    sample = "Explain the difference between a list and a tuple in Python."
    print("[model_interface] Generating sample...")
    print(generate(sample, max_new_tokens=200))
