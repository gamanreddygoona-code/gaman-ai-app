"""
parallel_progress_monitor.py
─────────────────────────────
Unified LIVE dashboard that connects to ALL 10 parallel training workers.
Reads each worker's checkpoint file every 2 seconds and renders a single
consolidated view with per-worker progress bars, speed, ETA, and grand total.
"""

import os
import sys
import json
import time
import shutil

# ── Config ────────────────────────────────────────────────────────────────
WORKERS = 5
TARGET_PER_WORKER = 20_000_000
TOTAL_TARGET = WORKERS * TARGET_PER_WORKER  # 100,000,000

CHECKPOINT_FILES = [f"checkpoint_worker_{i}.json" for i in range(WORKERS)]

WORKER_LABELS = {
    0: "C4-Part1",
    1: "C4-Part2",
    2: "C4-Part3",
    3: "C4-Part4",
    4: "C4-Part5"
}

# Track history for per-worker speed calculation
_prev_counts = {}
_prev_time = None


def read_worker_progress(worker_id):
    path = CHECKPOINT_FILES[worker_id]
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f).get("imported", 0)
        except (json.JSONDecodeError, KeyError, ValueError):
            return 0
    return 0


def format_time(seconds):
    if seconds < 0:
        return "--:--:--"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_number(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def make_bar(current, total, width=25):
    if total == 0:
        return "░" * width
    ratio = min(current / total, 1.0)
    filled = int(width * ratio)
    return "█" * filled + "░" * (width - filled)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    global _prev_counts, _prev_time

    start_time = time.time()
    _prev_time = start_time
    for i in range(WORKERS):
        _prev_counts[i] = read_worker_progress(i)

    try:
        while True:
            now = time.time()
            elapsed = now - start_time
            dt = now - _prev_time if _prev_time else 1

            # Collect current counts
            counts = {}
            speeds = {}
            for i in range(WORKERS):
                counts[i] = read_worker_progress(i)
                delta = counts[i] - _prev_counts.get(i, 0)
                speeds[i] = delta / dt if dt > 0 else 0

            grand_total = sum(counts.values())
            grand_speed = sum(speeds.values())
            grand_pct = grand_total / TOTAL_TARGET * 100

            # ── Render ────────────────────────────────────────────────
            clear_screen()

            term_width = shutil.get_terminal_size((80, 30)).columns
            sep = "═" * min(term_width, 76)

            print(sep)
            print("  📡  100 MILLION TRAINING — UNIFIED LIVE DASHBOARD")
            print(f"  ⏱️   Elapsed: {format_time(elapsed)}    |    "
                  f"Combined Speed: {grand_speed:,.0f} rec/s")
            print(sep)
            print()

            # Workers table header
            print(f"  {'#':>2}  {'Worker':<13} {'Progress Bar':<27} {'Done':>8} / {'Target':>8}   {'%':>6}   {'Speed':>9}   {'ETA':>9}   {'Status'}")
            print(f"  {'─'*2}  {'─'*13} {'─'*27} {'─'*8}   {'─'*8}   {'─'*6}   {'─'*9}   {'─'*9}   {'─'*7}")

            active_count = 0
            done_count = 0

            for i in range(WORKERS):
                c = counts[i]
                pct = c / TARGET_PER_WORKER * 100
                bar = make_bar(c, TARGET_PER_WORKER, 25)
                spd = speeds[i]
                label = WORKER_LABELS.get(i, f"Worker-{i}")

                if c >= TARGET_PER_WORKER:
                    status = "✅ DONE"
                    eta_str = "00:00:00"
                    done_count += 1
                elif c == 0:
                    status = "⏳ WAIT"
                    eta_str = "--------"
                else:
                    status = "🔄 RUN "
                    active_count += 1
                    if spd > 0:
                        remaining = TARGET_PER_WORKER - c
                        eta_str = format_time(remaining / spd)
                    else:
                        eta_str = "--------"

                spd_str = f"{spd:,.0f}/s" if spd > 0 else "---"

                print(f"  {i:>2}  {label:<13} [{bar}] {format_number(c):>8} / {format_number(TARGET_PER_WORKER):>8}   {pct:5.1f}%   {spd_str:>9}   {eta_str:>9}   {status}")

            # Grand total section
            print()
            print(f"  {'═' * min(term_width - 4, 72)}")

            grand_bar = make_bar(grand_total, TOTAL_TARGET, 40)
            print(f"  🎯  GRAND TOTAL  [{grand_bar}]  {grand_pct:5.1f}%")
            print(f"      {grand_total:>14,} / {TOTAL_TARGET:,} examples")
            print()

            if grand_speed > 0:
                remaining_total = TOTAL_TARGET - grand_total
                eta_total = remaining_total / grand_speed
                print(f"      ⚡ Combined:  {grand_speed:>8,.0f} records/sec")
                print(f"      ⏰ ETA:       {format_time(eta_total)}  (~{eta_total / 3600:.1f} hours)")
            else:
                print(f"      ⚡ Combined:  calculating...")
                print(f"      ⏰ ETA:       calculating...")

            print(f"      🟢 Active:    {active_count} workers")
            print(f"      ✅ Complete:   {done_count} / {WORKERS} workers")

            print()
            print(f"  {'═' * min(term_width - 4, 72)}")
            print("  Press Ctrl+C to stop monitoring (workers keep running in their terminals)")

            # Check if all done
            if done_count == WORKERS:
                print()
                print("  🎉🎉🎉  ALL 5 WORKERS COMPLETE!  100,000,000 EXAMPLES IMPORTED!  🎉🎉🎉")
                print()
                break

            # Save state for next speed calculation
            _prev_counts = counts.copy()
            _prev_time = now

            time.sleep(3)

    except KeyboardInterrupt:
        print("\n\n  👋  Monitor stopped. Workers continue running in their terminals.")
        print(f"  📊  Last seen total: {grand_total:,} / {TOTAL_TARGET:,}")


if __name__ == "__main__":
    main()
