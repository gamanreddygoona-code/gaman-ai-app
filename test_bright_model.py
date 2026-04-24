import asyncio
import os
from model_interface import generate

# Set environment variable to load a specific model if needed
# os.environ["GAMAN_MODEL_NAME"] = "meta-llama/Llama-2-7b-chat-hf"

def test_bright_prompt():
    user_msg = "Explain how a quantum computer works to a 10 year old, and write a simple python loop to simulate 10 qubits."
    
    # We construct the same prompt as app.py
    full_prompt = f"""<|system|>
You are Gaman AI — an advanced, highly intelligent assistant that rivals ChatGPT 4.5.
You are exceptionally bright, capable of deep reasoning, and expert-level coding.

## Instructions:
1. THINK step-by-step to arrive at the correct answer.
2. Provide complete, runnable code examples when asked about programming.
3. Be conversational and highly intelligent. Do not explicitly say 'Based on the provided information' or act robotic.

## Memory & Context:
<|user|>
{user_msg}
<|assistant|>"""

    print("="*60)
    print("🧠 TESTING THE NEW BRIGHT MODEL PROMPT")
    print("="*60)
    print(f"User: {user_msg}\n")
    
    print("⏳ Thinking...\n")
    # Generate the response using the local model
    response = generate(full_prompt, max_new_tokens=512)
    
    print("========================================")
    print("🤖 Gaman AI Response:")
    print("========================================")
    print(response)

if __name__ == "__main__":
    test_bright_prompt()
