"""
live_data_feed.py
──────────────────
Tails the shard databases and prints the latest 10 training examples
as they are added by the background workers.
"""

import sqlite3
import time
import os

SHARDS = [f"./shard_worker_{i}.db" for i in range(5)]

def get_latest_from_shard(db_path):
    if not os.path.exists(db_path):
        return []
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT user_message, bot_response FROM massive_training ORDER BY id DESC LIMIT 5")
        rows = cur.fetchall()
        conn.close()
        return rows
    except:
        return []

def main():
    print("=" * 80)
    print(" 🌊  LIVE DATA STREAM — 100M TRAINING FEED")
    print("     Showing the latest examples being ingested into the shards...")
    print("=" * 80)
    print()

    seen_messages = set()

    try:
        while True:
            for shard in SHARDS:
                rows = get_latest_from_shard(shard)
                for user, bot in rows:
                    msg_hash = hash(user[:100] + bot[:100])
                    if msg_hash not in seen_messages:
                        # Clean up for display
                        u = user.replace('\n', ' ')[:70]
                        b = bot.replace('\n', ' ')[:70]
                        
                        print(f" 📥 [DATA] Q: {u}...")
                        print(f"          A: {b}...")
                        print("-" * 80)
                        
                        seen_messages.add(msg_hash)
                        # Keep memory clean
                        if len(seen_messages) > 1000:
                            seen_messages.clear()
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n👋 Feed stopped.")

if __name__ == "__main__":
    main()
