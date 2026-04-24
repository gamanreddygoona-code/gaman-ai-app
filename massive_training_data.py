"""
massive_training_data.py
──────────────────────────
Downloads REAL training data from HuggingFace datasets.
Imports into SQLite for Gaman AI to search through.

Quick mode: ~400K examples (5-10 mins)
Full mode:  ~8M examples (1-2 hours)
"""

import os, sys, sqlite3, json, time

DB_PATH = "C:/Gamansai/ai/ai_data.db"


def check_deps():
    try:
        import datasets
        return True
    except ImportError:
        print("❌ Run first: pip install datasets")
        return False


def init_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS massive_training (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            source       TEXT,
            category     TEXT,
            quality      REAL DEFAULT 0.8
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mt_user ON massive_training(user_message)")
    conn.commit()
    conn.close()
    print("✅ Table ready")


def _import(rows, source, category, quality=0.85):
    conn = sqlite3.connect(DB_PATH)
    c = 0
    for user, bot in rows:
        if user and bot and len(user) > 5 and len(bot) > 10:
            conn.execute(
                "INSERT INTO massive_training (user_message, bot_response, source, category, quality) VALUES (?,?,?,?,?)",
                (user[:1500], bot[:2500], source, category, quality)
            )
            c += 1
            if c % 5000 == 0:
                conn.commit()
                print(f"  ✓ {c:,} rows...")
    conn.commit()
    conn.close()
    return c


def dl_alpaca():
    print("\n📥 Alpaca (52K instructions)...")
    try:
        from datasets import load_dataset
        ds = load_dataset("tatsu-lab/alpaca", split="train")
        rows = []
        for x in ds:
            instr = x.get("instruction","")
            inp   = x.get("input","")
            out   = x.get("output","")
            user  = f"{instr}\n{inp}".strip() if inp else instr
            rows.append((user, out))
        n = _import(rows, "alpaca", "instruction", 0.85)
        print(f"✅ Alpaca: {n:,}")
        return n
    except Exception as e:
        print(f"❌ {e}"); return 0


def dl_dolly():
    print("\n📥 Dolly-15K...")
    try:
        from datasets import load_dataset
        ds = load_dataset("databricks/databricks-dolly-15k", split="train")
        rows = [(x.get("instruction",""), x.get("response","")) for x in ds]
        n = _import(rows, "dolly", "human_written", 0.90)
        print(f"✅ Dolly: {n:,}")
        return n
    except Exception as e:
        print(f"❌ {e}"); return 0


def dl_code_alpaca():
    print("\n📥 CodeAlpaca (20K coding examples)...")
    try:
        from datasets import load_dataset
        ds = load_dataset("sahil2801/CodeAlpaca-20k", split="train")
        rows = []
        for x in ds:
            instr = x.get("instruction","")
            inp   = x.get("input","")
            out   = x.get("output","")
            user  = f"{instr}\n{inp}".strip() if inp else instr
            rows.append((user, out))
        n = _import(rows, "code_alpaca", "coding", 0.92)
        print(f"✅ CodeAlpaca: {n:,}")
        return n
    except Exception as e:
        print(f"❌ {e}"); return 0


def dl_openassistant():
    print("\n📥 OpenAssistant (80K human conversations)...")
    try:
        from datasets import load_dataset
        ds = load_dataset("OpenAssistant/oasst1", split="train")
        msgs = {x["message_id"]: x for x in ds}
        rows = []
        for mid, msg in msgs.items():
            if msg.get("role") == "assistant" and msg.get("parent_id"):
                parent = msgs.get(msg["parent_id"])
                if parent and parent.get("role") == "prompter" and msg.get("lang","en") == "en":
                    rows.append((parent.get("text",""), msg.get("text","")))
        n = _import(rows, "openassistant", "conversation", 0.95)
        print(f"✅ OpenAssistant: {n:,}")
        return n
    except Exception as e:
        print(f"❌ {e}"); return 0


def dl_wizardlm():
    print("\n📥 WizardLM (200K complex instructions)...")
    try:
        from datasets import load_dataset
        ds = load_dataset("WizardLMTeam/WizardLM_evol_instruct_V2_196k", split="train")
        rows = []
        for x in ds:
            convs = x.get("conversations", [])
            for i in range(0, len(convs)-1, 2):
                h, g = convs[i], convs[i+1]
                if h.get("from") == "human" and g.get("from") == "gpt":
                    rows.append((h.get("value",""), g.get("value","")))
        n = _import(rows, "wizardlm", "complex", 0.88)
        print(f"✅ WizardLM: {n:,}")
        return n
    except Exception as e:
        print(f"❌ {e}"); return 0


def quick_mode():
    """Quick import: ~400K examples in ~10 minutes."""
    print("=" * 60)
    print("⚡ QUICK MODE — ~400K examples")
    print("=" * 60)
    init_table()
    total = 0
    total += dl_alpaca()
    total += dl_dolly()
    total += dl_code_alpaca()
    total += dl_openassistant()
    total += dl_wizardlm()
    print("\n" + "=" * 60)
    print(f"🎉 DONE: {total:,} examples imported!")
    print("=" * 60)
    show_stats()


def full_mode():
    """Full import: 8M+ examples (1-2 hours)."""
    quick_mode()
    print("\n📥 Streaming large datasets...")
    try:
        from datasets import load_dataset
        ds = load_dataset("stingning/ultrachat", split="train", streaming=True)
        rows = []
        for i, x in enumerate(ds):
            if i >= 200000: break
            data = x.get("data", [])
            for j in range(0, len(data)-1, 2):
                rows.append((str(data[j])[:1500], str(data[j+1])[:2500]))
            if len(rows) >= 5000:
                _import(rows, "ultrachat", "conversation", 0.82)
                rows = []
                print(f"  ✓ UltraChat batch {i:,}...")
        if rows: _import(rows, "ultrachat", "conversation", 0.82)
        print("✅ UltraChat done")
    except Exception as e:
        print(f"❌ UltraChat: {e}")
    show_stats()


def show_stats():
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM massive_training").fetchone()[0]
    rows  = conn.execute("SELECT source, COUNT(*) FROM massive_training GROUP BY source ORDER BY 2 DESC").fetchall()
    conn.close()
    print(f"\n📊 Total: {total:,} training examples")
    for src, cnt in rows:
        print(f"  • {src:<20} {cnt:>10,}")


if __name__ == "__main__":
    if not check_deps(): sys.exit(1)
    mode = sys.argv[1] if len(sys.argv) > 1 else "--quick"
    if mode == "--full":
        full_mode()
    elif mode == "--stats":
        show_stats()
    else:
        quick_mode()
