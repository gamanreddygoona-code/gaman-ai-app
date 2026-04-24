import sqlite3
import re

DB_PATH = "./ai_data.db"
SOURCE = "master_teaching"

# Massive dataset of smart, fast, and high-quality responses
MASTER_DATA = [
    # ADVANCED CODING: WEB APPS
    ("create a full website", """Absolutely! Here is a complete, high-performance, responsive single-page website template using modern HTML5 and Vanilla CSS. No external frameworks needed—pure, fast code. 🚀

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GamanAI Premium Showcase</title>
    <style>
        :root {
            --primary: #6366f1;
            --dark: #0f172a;
            --light: #f8fafc;
            --glass: rgba(255, 255, 255, 0.1);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background: var(--dark); color: var(--light); overflow-x: hidden; }
        
        header {
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
            text-align: center;
        }
        
        .hero h1 {
            font-size: 5rem;
            background: linear-gradient(to right, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            animation: fadeIn 1.5s ease-out;
        }
        
        .hero p { font-size: 1.5rem; color: #94a3b8; margin-bottom: 2rem; }
        
        .btn {
            padding: 1rem 2.5rem;
            background: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            transition: 0.3s;
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 20px 35px -5px rgba(99, 102, 241, 0.5); }
        
        section { padding: 100px 10%; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .card {
            background: var(--glass);
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            transition: 0.3s;
        }
        .card:hover { transform: translateY(-10px); background: rgba(255,255,255,0.15); }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <header>
        <div class="hero">
            <h1>Next-Gen AI Experience</h1>
            <p>Locally powered. Privacy focused. Smartly built.</p>
            <a href="#features" class="btn">Explore Features</a>
        </div>
    </header>
    
    <section id="features">
        <div class="grid">
            <div class="card">
                <h3>High Speed</h3>
                <p>Built for zero latency. Everything runs on your hardware, no cloud delays.</p>
            </div>
            <div class="card">
                <h3>Secure</h3>
                <p>Your data never leaves your machine. 100% privacy by design.</p>
            </div>
            <div class="card">
                <h3>Intelligent</h3>
                <p>Trained on millions of examples to provide world-class assistance.</p>
            </div>
        </div>
    </section>
</body>
</html>
```

**Instruction:**
1. Save this as `index.html`.
2. Open it in any browser.
3. You now have a premium, dark-mode, animated landing page! 🚀""", 0.99),

    # FAST CODE: PYTHON UTILITIES
    ("write a scraper", """Here is a hyper-fast, clean Python scraper using `requests` and `BeautifulSoup`. 🐍

```python
import requests
from bs4 import BeautifulSoup

def quick_scrape(url):
    print(f"🚀 Scraping: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title and all H1s
        title = soup.title.string if soup.title else "No Title"
        h1s = [h1.get_text() for h1 in soup.find_all('h1')]
        
        return {
            "status": "success",
            "title": title,
            "headings": h1s
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Usage
res = quick_scrape("https://example.com")
print(res)
```

Need to scrape something specific? Just tell me the URL!""", 0.98),

    # SMART TALK: AI PHILOSOPHY
    ("what is the future of ai", """The future of AI isn't just about 'big clouds' like ChatGPT. It's about **Local Intelligence**. 🧠

Imagine an AI that:
1. **Knows you perfectly** because it reads your local files (securely).
2. **Works offline** so you're never disconnected from your tools.
3. **Is yours**—you own the weights, the data, and the hardware.

We are moving towards 'Edge AI' where every device has a brain. This protects privacy and democratizes power. You are at the forefront of that right now by running me! 🚀""", 0.97),

    # SMARTER RESPONSES: PROBLEM SOLVING
    ("my code is slow", """Optimization is an art! Here are the **Big 3** ways to speed up Python code instantly: ⚡

1. **Vectorization**: Use `numpy` instead of loops for math.
2. **Built-ins**: `map()`, `filter()`, and list comprehensions are implemented in C and much faster than `for` loops.
3. **Profiling**: Use `cProfile` to find exactly which line is taking the most time.

**Try this swap:**
❌ *Slow:* `for x in range(1000): list.append(x**2)`
✅ *Fast:* `[x**2 for x in range(1000)]`

Paste your code here and I'll optimize it for you! 🔧""", 0.98),

    # FAST CODE: FASTAPI
    ("create an api", """FastAPI is my favorite! Here is a 'Hello World' API that you can run in 3 seconds. ⚡

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "online", "message": "GamanAI API is active!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "category": "General"}

# Run with: uvicorn main:app --reload
```

It's fast, auto-validates data, and generates documentation at `/docs` instantly. Want me to add a database connection? 💾""", 0.99),

    # PERSONALITY: WHY LOCAL?
    ("why use you instead of chatgpt", """Great question! Here's why I'm your best companion: 🛡️

1. **Zero Data Leaks**: Every word we speak stays on your hard drive. 
2. **Permanent Memory**: I don't reset every session. Everything you teach me, I remember forever in your local SQLite database.
3. **No Subscription**: I don't cost $20/month. I use your own hardware.
4. **Offline Access**: I work in a basement, on a plane, or in the woods. 🌲

I am **your** AI. Not a service you rent. 🤖""", 0.98),
]

def teach_master_dataset():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS learned_knowledge (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, content TEXT, source TEXT, confidence REAL, created_at TEXT DEFAULT (datetime('now')))")
    
    total = len(MASTER_DATA)
    saved = 0
    
    for topic, content, confidence in MASTER_DATA:
        # Check if exists (by topic)
        existing = conn.execute("SELECT id FROM learned_knowledge WHERE topic=?", (topic,)).fetchone()
        if existing:
            conn.execute("UPDATE learned_knowledge SET content=?, source=?, confidence=?, created_at=datetime('now') WHERE id=?", 
                         (content, SOURCE, confidence, existing[0]))
        else:
            conn.execute("INSERT INTO learned_knowledge (topic, content, source, confidence) VALUES (?, ?, ?, ?)", 
                         (topic, content, SOURCE, confidence))
        saved += 1
        print(f"  [{saved}/{total}] 🧠 Taught: {topic}")
        
    conn.commit()
    conn.close()
    print(f"\n✅ MASTER TEACHING COMPLETE: {saved} elite responses added.")

if __name__ == "__main__":
    teach_master_dataset()
