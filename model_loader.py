"""
model_loader.py
───────────────
Lazy-loading model engine for Gaman AI.
Model loads only when first needed — never crashes on import.
"""

import os

MODEL_ID   = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
CACHE_DIR  = "C:/Users/vijay/.cache/huggingface/hub"
MODEL_MODE = "smart-local"   # Default until model loads

_pipe      = None   # Lazy-loaded
_load_tried = False


def _load():
    global _pipe, MODEL_MODE, _load_tried
    if _load_tried:
        return
    _load_tried = True
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[model_loader] Loading {MODEL_ID} on {device}...")
        tok = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)
        mdl = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            cache_dir=CACHE_DIR,
            dtype=torch.float32 if device == "cpu" else torch.float16,
            device_map=device,
        )
        _pipe = pipeline("text-generation", model=mdl, tokenizer=tok,
                         device=0 if device == "cuda" else -1)
        MODEL_MODE = "tiny-llama-local"
        print(f"[model_loader] ✅ TinyLlama ready")
    except Exception as e:
        print(f"[model_loader] ⚠️  Model skipped ({e}). Using smart-local engine.")
        MODEL_MODE = "smart-local"


def generate_response(prompt: str, max_new_tokens: int = 256,
                      user_message: str | None = None) -> str:
    """Generate response — uses TinyLlama if loaded, else smart_local_engine."""
    _load()

    if _pipe:
        try:
            fmt = (f"<|system|>\nYou are Gaman AI, a world-class coding assistant."
                   f"</s>\n<|user|>\n{user_message or prompt}</s>\n<|assistant|>\n")
            out = _pipe(fmt, max_new_tokens=max_new_tokens,
                        do_sample=True, temperature=0.7,
                        top_k=50, top_p=0.95)
            result = out[0]["generated_text"]
            if "<|assistant|>\n" in result:
                result = result.split("<|assistant|>\n")[-1].strip()
            return result
        except Exception as e:
            print(f"[model_loader] Generation error: {e}")

    # Fallback to smart local engine
    from smart_local_engine import smart_local_response
    return smart_local_response(user_message or prompt)


print(f"[model_loader] ✅ Engine ready (lazy load, mode: {MODEL_MODE})")
