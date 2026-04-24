import os
import sqlite3

DB_PATH = "./ai_data.db"
SOURCE = "self_awareness"

def teach_self_architecture():
    conn = sqlite3.connect(DB_PATH)
    files = [f for f in os.listdir('.') if f.endswith('.py')]
    
    print(f"🧩 Teaching self-architecture from {len(files)} files...")
    
    for filename in files:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Create a summary topic for each file
            topic = f"How {filename} works"
            summary = f"File: {filename}\nDescription: Part of the Gaman AI core architecture.\n\nCode Analysis:\n{content[:2000]}" # Store first 2k chars
            
            conn.execute("""
                INSERT OR REPLACE INTO learned_knowledge (topic, content, source, confidence)
                VALUES (?, ?, ?, ?)
            """, (topic, summary, SOURCE, 1.0))
            
    # Add a general self-awareness topic
    awareness_text = """I am Gaman AI, a high-performance local AI system. 
My architecture consists of:
- FastAPI Backend (app.py)
- SQLite Knowledge Base (ai_data.db)
- Autonomous World Trainer (world_trainer.py)
- Smart Response Engine (learning_system.py)
- AAA Game Generation Engine (aaa_game_engine.py)

I am 100% private, locally hosted, and capable of autonomous web learning."""
    
    conn.execute("""
        INSERT OR REPLACE INTO learned_knowledge (topic, content, source, confidence)
        VALUES (?, ?, ?, ?)
    """, ("who are you really", awareness_text, SOURCE, 1.0))
    
    conn.commit()
    conn.close()
    print("✅ Self-awareness training complete!")

if __name__ == "__main__":
    teach_self_architecture()
