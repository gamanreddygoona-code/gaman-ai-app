"""
train_model.py
──────────────
Trains a LoRA adapter on CodeLlama-7b-Instruct using sample coding data.
After training, the adapter is saved to ./fine-tuned-coding-model/

Run:  python train_model.py
Requires: GPU with >= 8 GB VRAM
"""

import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# ── Config ───────────────────────────────────────────────────
BASE_MODEL   = "codellama/CodeLlama-7b-Instruct-hf"
OUTPUT_DIR   = "./fine-tuned-coding-model"
EPOCHS       = 3
BATCH_SIZE   = 2
LEARNING_RATE = 2e-4

# ── Sample training data (coding Q&A pairs) ─────────────────
training_data = [
    {"text": "[INST] Write a Python function to add two numbers. [/INST] Here's a simple function:\n\n```python\ndef add(a, b):\n    return a + b\n\n# Example\nresult = add(3, 5)\nprint(result)  # Output: 8\n```"},
    {"text": "[INST] How do I read a file in Python? [/INST] You can read a file like this:\n\n```python\nwith open('myfile.txt', 'r') as f:\n    content = f.read()\n    print(content)\n```\n\nUsing `with` ensures the file is automatically closed."},
    {"text": "[INST] Write a for loop that prints 1 to 10. [/INST] Here you go:\n\n```python\nfor i in range(1, 11):\n    print(i)\n```\n\nThis prints numbers 1 through 10."},
    {"text": "[INST] How do I connect to SQLite in Python? [/INST] Use the built-in sqlite3 module:\n\n```python\nimport sqlite3\n\nconn = sqlite3.connect('mydb.db')\ncursor = conn.cursor()\ncursor.execute('SELECT * FROM my_table')\nrows = cursor.fetchall()\nfor row in rows:\n    print(row)\nconn.close()\n```"},
    {"text": "[INST] Explain what a list is in Python. [/INST] A list is an ordered collection of items. You can store different types of data in a list.\n\n```python\nfruits = ['apple', 'banana', 'cherry']\nprint(fruits[0])    # apple\nfruits.append('date')\nprint(len(fruits))  # 4\n```\n\nLists are mutable — you can add, remove, and change items."},
    {"text": "[INST] Write a function that checks if a number is even or odd. [/INST] Here's the function:\n\n```python\ndef check_even_odd(n):\n    if n % 2 == 0:\n        return 'Even'\n    else:\n        return 'Odd'\n\nprint(check_even_odd(7))   # Odd\nprint(check_even_odd(10))  # Even\n```"},
    {"text": "[INST] How do I create a dictionary in Python? [/INST] A dictionary stores key-value pairs:\n\n```python\nstudent = {\n    'name': 'Alice',\n    'age': 20,\n    'grade': 'A'\n}\n\nprint(student['name'])   # Alice\nstudent['age'] = 21      # Update a value\n```"},
    {"text": "[INST] Write a Python class for a simple calculator. [/INST] Here's a clean calculator class:\n\n```python\nclass Calculator:\n    def add(self, a, b):\n        return a + b\n\n    def subtract(self, a, b):\n        return a - b\n\n    def multiply(self, a, b):\n        return a * b\n\n    def divide(self, a, b):\n        if b == 0:\n            return 'Cannot divide by zero'\n        return a / b\n\ncalc = Calculator()\nprint(calc.add(10, 5))       # 15\nprint(calc.divide(10, 3))    # 3.333...\n```"},
    {"text": "[INST] How do I handle errors in Python? [/INST] Use try-except blocks:\n\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print('Cannot divide by zero!')\nexcept Exception as e:\n    print(f'An error occurred: {e}')\nfinally:\n    print('This always runs.')\n```"},
    {"text": "[INST] Write a FastAPI hello world. [/INST] Here's a minimal FastAPI app:\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello, World!'}\n```\n\nRun it with: `uvicorn main:app --reload`\nThen visit: http://127.0.0.1:8000"},
    {"text": "[INST] Write a JavaScript hello world program. [/INST] Sure, here is a clean example:\n\n```javascript\nconsole.log('Hello, World!');\n```\n\nRun it with Node.js using `node app.js`."},
    {"text": "[INST] Show a TypeScript function to reverse a string. [/INST] Here is a simple TypeScript example:\n\n```typescript\nfunction reverseString(value: string): string {\n  return value.split('').reverse().join('');\n}\n\nconsole.log(reverseString('hello'));\n```\n\nThe function splits the string into characters, reverses them, and joins them back together."},
    {"text": "[INST] Write a Java hello world program. [/INST] Here you go:\n\n```java\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}\n```\n\nCompile with `javac Main.java` and run with `java Main`."},
    {"text": "[INST] Show a C++ function to add two integers. [/INST] Here's a clean C++ example:\n\n```cpp\n#include <iostream>\n\nint add(int a, int b) {\n    return a + b;\n}\n\nint main() {\n    std::cout << add(2, 3) << std::endl;\n    return 0;\n}\n```\n\nThis defines a reusable function and prints the result."},
    {"text": "[INST] How do I read a file in Rust? [/INST] You can use `std::fs::read_to_string`:\n\n```rust\nuse std::fs;\n\nfn main() {\n    let content = fs::read_to_string(\"example.txt\").expect(\"failed to read file\");\n    println!(\"{}\", content);\n}\n```\n\nThis reads the whole file into a string and prints it."},
    {"text": "[INST] Show a Go API endpoint example. [/INST] Here's a minimal Go server:\n\n```go\npackage main\n\nimport (\n    \"encoding/json\"\n    \"net/http\"\n)\n\nfunc hello(w http.ResponseWriter, r *http.Request) {\n    w.Header().Set(\"Content-Type\", \"application/json\")\n    json.NewEncoder(w).Encode(map[string]string{\"message\": \"hello\"})\n}\n\nfunc main() {\n    http.HandleFunc(\"/hello\", hello)\n    http.ListenAndServe(\":3000\", nil)\n}\n```\n\nIt exposes one endpoint that returns JSON."},
    {"text": "[INST] Show a SQL query to list all tables. [/INST] Use this query in SQLite:\n\n```sql\nSELECT name\nFROM sqlite_master\nWHERE type = 'table'\nORDER BY name;\n```\n\nIt returns every table name in the current database."},
    {"text": "[INST] Explain what an API is. [/INST] An API is a way for one program to talk to another through a defined set of rules.\n\nA web API usually works like this:\n1. A client sends a request.\n2. The server processes it.\n3. The server returns a response, often JSON.\n\nFor example, a weather app might call an API to get today's forecast."},
    {"text": "[INST] How should you talk to a beginner programmer? [/INST] Use simple language, answer directly, avoid unnecessary jargon, and include a small working example. If there is a tricky term, explain it in one sentence before moving on."},
]

print("=" * 55)
print("   🎯  LoRA Fine-Tuning — CodeLlama-7b-Instruct")
print("=" * 55)

# ── Check GPU ────────────────────────────────────────────────
if not torch.cuda.is_available():
    print("\n❌ No GPU detected! LoRA training requires a CUDA GPU.")
    print("   If you have an NVIDIA GPU, install the CUDA version of PyTorch:")
    print("   pip install torch --index-url https://download.pytorch.org/whl/cu121")
    exit(1)

print(f"\n✅ GPU: {torch.cuda.get_device_name(0)}")
print(f"   VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")

# ── Load tokenizer ───────────────────────────────────────────
print("\n[1/5] Loading tokenizer ...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token

# ── Load base model in 4-bit ─────────────────────────────────
print("[2/5] Loading base model (4-bit quantization) ...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
)

model = prepare_model_for_kbit_training(model)

# ── Attach LoRA ──────────────────────────────────────────────
print("[3/5] Configuring LoRA adapter ...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ── Prepare dataset ──────────────────────────────────────────
print("[4/5] Preparing training dataset ...")
dataset = Dataset.from_list(training_data)

# ── Train ────────────────────────────────────────────────────
print("[5/5] Starting training ...\n")

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=2,
    learning_rate=LEARNING_RATE,
    fp16=True,
    logging_steps=1,
    save_strategy="epoch",
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=512,
)

trainer.train()

# ── Save adapter ─────────────────────────────────────────────
print(f"\n💾 Saving LoRA adapter to {OUTPUT_DIR}/ ...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n" + "=" * 55)
print("   ✅  Training complete!")
print(f"   📁  Adapter saved to: {OUTPUT_DIR}/")
print("   🚀  Now restart the chatbot: python -m uvicorn app:app --reload")
print("=" * 55)
