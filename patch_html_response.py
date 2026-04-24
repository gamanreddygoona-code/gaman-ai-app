import sqlite3

DB_PATH = "./ai_data.db"

def update_html_response():
    conn = sqlite3.connect(DB_PATH)
    
    html_template = """Absolutely! Here is a clean, modern HTML5 boilerplate to get you started. 🚀

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Awesome Website</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f9;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; }
        p { color: #555; }
        .btn {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to My Website! 🌐</h1>
        <p>This is a simple, clean website built with HTML and CSS.</p>
        <p>HTML provides the structure, and CSS makes it look beautiful.</p>
        <a href="#" class="btn">Click Me!</a>
    </div>
</body>
</html>
```

**How to use this:**
1. Copy the code above.
2. Create a new file named `index.html`.
3. Paste the code and save.
4. Open the file in your browser!

Want me to add more features like a navigation bar or a contact form? Just ask! 💪"""

    topic = 'create a website using html'
    
    # Check if exists
    cursor = conn.execute("SELECT id FROM learned_knowledge WHERE topic = ?", (topic,))
    row = cursor.fetchone()
    
    if row:
        conn.execute("UPDATE learned_knowledge SET content = ?, confidence = 0.99 WHERE id = ?", (html_template, row[0]))
        print(f"✅ Updated existing topic: {topic}")
    else:
        conn.execute("INSERT INTO learned_knowledge (topic, content, source, confidence) VALUES (?, ?, ?, ?)", 
                     (topic, html_template, 'deep_teaching', 0.99))
        print(f"✅ Created new topic: {topic}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_html_response()
