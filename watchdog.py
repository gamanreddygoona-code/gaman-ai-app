"""
watchdog.py
───────────
Protector: Monitors ONLY the hyperfast training workers.
Does NOT touch servers — only checks and auto-recovers crashed workers.
"""

import os
import sys
import time
import subprocess

try:
    import psutil
except ImportError:
    print("Installing psutil...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

WORKER_SCRIPT = "hyperfast_worker.py"
AI_DIR        = r"c:\Gamansai\ai"
EXPECTED_WORKERS = set(range(5))  # Workers 0-4


def find_active_workers():
    """Find which worker IDs are currently alive."""
    active = set()
    for p in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmd = " ".join(p.info.get('cmdline') or [])
            if WORKER_SCRIPT in cmd and "--worker" in cmd:
                parts = cmd.split("--worker")
                if len(parts) > 1:
                    w_str = parts[1].strip().split()[0]
                    if w_str.isdigit():
                        active.add(int(w_str))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return active


def relaunch_worker(worker_id):
    print(f"[Watchdog] ⚠️  Worker {worker_id} DOWN — relaunching...")
    subprocess.Popen(
        ["powershell", "-NoExit", "-Command",
         f"cd '{AI_DIR}'; $Host.UI.RawUI.WindowTitle='⚡ WORKER {worker_id} (RELAUNCHED)';"
         f"Write-Host 'WORKER {worker_id} RELAUNCHED' -ForegroundColor Yellow;"
         f"python {WORKER_SCRIPT} --worker {worker_id}"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )


def main():
    print("=" * 62)
    print("  🐕  GAMANSAI WATCHDOG — WORKERS ONLY")
    print(f"  Monitoring: {WORKER_SCRIPT} (workers 0-4)")
    print("  ❌ Server checking DISABLED — workers only")
    print("  Auto-heals crashed workers every 60 seconds.")
    print("=" * 62)

    while True:
        try:
            now = time.strftime("%H:%M:%S")
            active = find_active_workers()
            missing = EXPECTED_WORKERS - active

            if missing:
                for w in sorted(missing):
                    relaunch_worker(w)
                    time.sleep(2)  # Stagger relaunches
            else:
                print(f"[{now}] ✅ All {len(active)} workers healthy")

        except Exception as e:
            print(f"[Watchdog Error] {e}")

        time.sleep(60)

if __name__ == "__main__":
    main()
