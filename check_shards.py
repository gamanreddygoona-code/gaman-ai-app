import sqlite3, os

total = 0
for i in range(10):
    db = f'shard_worker_{i}.db'
    if not os.path.exists(db):
        continue
    size_gb = os.path.getsize(db) / (1024**3)
    try:
        conn = sqlite3.connect(db, timeout=10)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        if tables:
            tbl = tables[0][0]
            count = conn.execute(f'SELECT COUNT(*) FROM "{tbl}"').fetchone()[0]
            total += count
            sample = conn.execute(f'SELECT * FROM "{tbl}" LIMIT 1').fetchone()
            cols = [d[0] for d in conn.execute(f'SELECT * FROM "{tbl}" LIMIT 0').description]
            print(f'shard_{i}: {count:,} rows | {size_gb:.2f} GB | table={tbl} | cols={cols}')
        else:
            print(f'shard_{i}: {size_gb:.2f} GB | NO TABLES')
        conn.close()
    except Exception as e:
        print(f'shard_{i}: {size_gb:.2f} GB | ERROR: {e}')

print(f'\nTOTAL RECORDS: {total:,}')
