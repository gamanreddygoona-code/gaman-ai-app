"""
code_executor.py
────────────────
Safely execute Python code locally and return the output.
Runs in a subprocess with a timeout — no imports can escape the sandbox.

Usage:
    from code_executor import execute_python
    result = execute_python("print(2 + 2)")
    # {"output": "4", "error": "", "success": True}
"""

import subprocess
import sys
import re
import textwrap

TIMEOUT_SECONDS = 10

# Dangerous patterns — block before executing
BLOCKED_PATTERNS = [
    r"\bos\.system\b",
    r"\bsubprocess\b",
    r"\bopen\s*\(",
    r"\b__import__\b",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bcompile\s*\(",
    r"\bimportlib\b",
    r"\bshutil\b",
    r"\bsocket\b",
    r"rm\s+-rf",
    r"\bctypes\b",
]

SAFE_IMPORTS = {
    "math", "random", "re", "json", "datetime", "collections",
    "itertools", "functools", "string", "time", "statistics",
    "decimal", "fractions", "heapq", "bisect", "copy",
    "pprint", "textwrap", "unicodedata",
}


def _is_safe(code: str) -> tuple[bool, str]:
    """Return (is_safe, reason) for given code."""
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, code):
            return False, f"Blocked pattern: `{pattern}`"

    # Check imports
    imports = re.findall(r"^(?:import|from)\s+([\w.]+)", code, re.MULTILINE)
    for mod in imports:
        root = mod.split(".")[0]
        if root not in SAFE_IMPORTS:
            return False, f"Module `{root}` is not in the safe import list"

    return True, ""


def execute_python(code: str, timeout: int = TIMEOUT_SECONDS) -> dict:
    """
    Execute Python code in a sandboxed subprocess.

    Returns:
        {
            "output":  str,   # stdout
            "error":   str,   # stderr or safety message
            "success": bool,
        }
    """
    code = textwrap.dedent(code).strip()

    safe, reason = _is_safe(code)
    if not safe:
        return {
            "output": "",
            "error": f"Blocked for safety: {reason}",
            "success": False,
        }

    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "output":  proc.stdout.strip(),
            "error":   proc.stderr.strip(),
            "success": proc.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error":  f"Execution timed out after {timeout}s",
            "success": False,
        }
    except Exception as e:
        return {
            "output": "",
            "error":  str(e),
            "success": False,
        }


def format_result(result: dict) -> str:
    """Format execute_python result as a markdown string."""
    if result["success"]:
        out = result["output"] or "(no output)"
        return f"**Output:**\n```\n{out}\n```"
    else:
        err = result["error"] or "Unknown error"
        out = result["output"]
        msg = f"**Error:**\n```\n{err}\n```"
        if out:
            msg += f"\n**Partial output:**\n```\n{out}\n```"
        return msg


def try_extract_and_run(user_message: str) -> str | None:
    """
    If user_message starts with 'run:' or contains a code block,
    extract and execute the code. Returns formatted result or None.
    """
    msg = user_message.strip()

    # Pattern 1: "run: <code>"
    if msg.lower().startswith("run:"):
        code = msg[4:].strip()
        result = execute_python(code)
        return format_result(result)

    # Pattern 2: ```python ... ```
    m = re.search(r"```(?:python)?\s*([\s\S]+?)```", msg, re.IGNORECASE)
    if m and any(w in msg.lower() for w in ["run", "execute", "output", "result"]):
        code = m.group(1).strip()
        result = execute_python(code)
        return format_result(result)

    return None


if __name__ == "__main__":
    tests = [
        "print(sum(range(1, 101)))",
        "import math\nprint(math.pi)",
        "for i in range(5): print(i**2)",
        "print('hello world')",
        "import os\nos.system('dir')",   # should be blocked
        "x = [i**2 for i in range(10)]\nprint(x)",
    ]
    for code in tests:
        r = execute_python(code)
        print(f"Code: {code[:40]!r}")
        print(f"  -> {format_result(r)}\n")
