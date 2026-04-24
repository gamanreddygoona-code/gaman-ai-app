"""
code_editor.py
──────────────
AI-powered code editor that understands file context.
Reads files, generates edits, shows diffs, applies changes.
Works like Codex editing files in real IDE.
"""

import os
import difflib
from pathlib import Path
import local_llm

def read_file(filepath: str) -> dict:
    """Read a file with context."""
    try:
        p = Path(filepath)
        if not p.exists():
            return {"error": f"File not found: {filepath}", "content": ""}

        content = p.read_text()
        lines = content.split("\n")

        return {
            "filepath": filepath,
            "content": content,
            "lines": lines,
            "line_count": len(lines),
            "language": p.suffix.lstrip(".") or "text",
        }
    except Exception as e:
        return {"error": str(e), "content": ""}


def generate_edit(filepath: str, request: str) -> dict:
    """
    AI generates code edits for a file.
    Reads file, understands context, generates modified version.
    """
    file_info = read_file(filepath)

    if file_info.get("error"):
        return {"error": file_info["error"], "success": False}

    original = file_info["content"]
    lang = file_info["language"]

    # Build context prompt
    context = f"""FILE: {filepath}
LANGUAGE: {lang}
LINES: {file_info['line_count']}

CURRENT CONTENT:
```{lang}
{original}
```

REQUEST: {request}

Generate ONLY the COMPLETE MODIFIED FILE CONTENT.
Keep the same structure. Show all changes clearly.
Return only the code, no explanation."""

    # Generate modified code
    modified = local_llm.generate(context, max_tokens=2048)

    if not modified:
        return {
            "error": "Code generation failed",
            "success": False,
        }

    # Generate diff
    orig_lines = original.split("\n")
    mod_lines = modified.split("\n")

    diff = list(difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile=f"{filepath} (original)",
        tofile=f"{filepath} (modified)",
        lineterm=""
    ))

    return {
        "success": True,
        "filepath": filepath,
        "original": original,
        "modified": modified,
        "diff": "\n".join(diff),
        "changes": len([l for l in diff if l.startswith("+") or l.startswith("-")]),
    }


def apply_edit(filepath: str, modified_content: str) -> dict:
    """
    Apply the AI-generated edits to the actual file.
    Saves backup first.
    """
    try:
        p = Path(filepath)

        # Backup original
        backup_path = f"{filepath}.backup"
        if p.exists():
            p.write_text(p.read_text())  # Read original
            Path(backup_path).write_text(p.read_text())

        # Write modified
        p.write_text(modified_content)

        return {
            "success": True,
            "filepath": filepath,
            "backup": backup_path,
            "message": f"File updated. Backup: {backup_path}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def generate_new_file(filename: str, request: str, language: str = "python") -> dict:
    """
    Generate a completely new file from scratch.
    """
    prompt = f"""Create a new {language} file named: {filename}

REQUEST: {request}

Generate COMPLETE, WORKING {language} code.
Include:
- All necessary imports
- Complete implementation
- Error handling
- Clear comments for complex parts

Return ONLY the code, no explanation:"""

    code = local_llm.generate(prompt, max_tokens=2048)

    if not code:
        return {
            "error": "Code generation failed",
            "success": False,
        }

    return {
        "success": True,
        "filename": filename,
        "code": code,
        "preview": code[:500],
    }


def understand_project(project_dir: str = ".") -> dict:
    """
    Understand project structure (like VSCode).
    Returns file tree and language stats.
    """
    try:
        files = []
        for root, dirs, filenames in os.walk(project_dir):
            # Skip hidden and cache dirs
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for fname in filenames:
                if fname.startswith("."):
                    continue

                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, project_dir)

                try:
                    size = os.path.getsize(fpath)
                    files.append({
                        "path": rel_path,
                        "size": size,
                        "ext": Path(fpath).suffix,
                    })
                except:
                    pass

        # Language stats
        ext_counts = {}
        for f in files:
            ext = f["ext"] or "other"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

        return {
            "project_dir": project_dir,
            "file_count": len(files),
            "files": files[:50],  # First 50
            "language_stats": ext_counts,
        }
    except Exception as e:
        return {"error": str(e)}


def generate_with_context(request: str, context_files: list[str] = None) -> dict:
    """
    Generate code with awareness of existing files.
    Like Codex editing with project context.
    """
    context = "PROJECT CONTEXT:\n\n"

    if context_files:
        for fpath in context_files[:5]:  # Max 5 files for context
            file_info = read_file(fpath)
            if not file_info.get("error"):
                context += f"FILE: {fpath}\n```\n{file_info['content'][:500]}\n```\n\n"

    context += f"\nREQUEST: {request}\n\nGenerate code that fits this project context."

    code = local_llm.generate(context, max_tokens=2048)

    return {
        "code": code,
        "context_files": context_files or [],
    }


if __name__ == "__main__":
    # Test
    print("Project structure:")
    proj = understand_project(".")
    print(f"Files: {proj['file_count']}")
    print(f"Languages: {proj['language_stats']}")
