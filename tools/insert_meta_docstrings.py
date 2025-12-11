#!/usr/bin/env python3
"""
Insert a `@meta` line at the start of every class/function docstring.

Rules:
- After the opening triple-quotes (`\""" or `'''`) insert a newline, `@meta`, newline, then the original docstring content.
- Preserve indentation and quote style (prefixes like r, f are preserved if detectable).
- If no docstring exists, add a new docstring with `@meta` as the sole line.
- Skip modifying this script file itself.

Usage: run from repository root; script modifies .py files in-place.
"""
from __future__ import annotations

import ast
import os
import re
import sys
from typing import List, Tuple


def find_python_files(root: str) -> List[str]:
    pyfiles = []
    for dirpath, dirnames, filenames in os.walk(root):
        # skip common binary/venv/cache dirs
        if any(part in (".git", "__pycache__", "venv", "env", "node_modules") for part in dirpath.split(os.sep)):
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                pyfiles.append(os.path.join(dirpath, fn))
    return pyfiles


def insert_meta_into_file(path: str, self_path: str) -> bool:
    # don't modify this file itself
    if os.path.abspath(path) == os.path.abspath(self_path):
        return False
    
    if "tools" in path:
        return False

    try:
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
    except (UnicodeDecodeError, OSError):
        return False

    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False

    lines = src.splitlines()
    edits: List[Tuple[int, int, List[str]]] = []  # start, end (inclusive), replacement lines

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if not node.body:
            continue

        first = node.body[0]

        if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) and isinstance(first.value.value, str):
            # existing docstring
            start = first.lineno - 1
            end = getattr(first, "end_lineno", start) - 1
            text_asm = "".join(lines[start:end])
            if "@meta" in text_asm or "@author" in text_asm:
                continue
            # try to detect prefix and quote from the opening line
            opening_line = lines[start] if start < len(lines) else ""
            m = re.match(r"^(?P<indent>\s*)(?P<prefix>[rubfRUBF]*)(?P<quote>'{3}|\"{3})", opening_line)
            if m:
                indent = m.group("indent")
                prefix = m.group("prefix")
                quote = m.group("quote")
            else:
                # fallback
                indent = re.match(r"^(\s*)", opening_line).group(1)
                prefix = ""
                quote = '"""'

            # use AST-provided docstring value (unescaped) to preserve logical content
            orig = first.value.value
            new_block: List[str] = []
            new_block.append(f"{indent}{prefix}{quote}")
            new_block.append(f"{indent}@meta\n")
            # new_block.append(f"{indent}{prefix}{quote}")
            # new_block.append(f"{indent}@meta")
            first = True
            if orig:
                for ln in orig.splitlines():
                    if first:
                        new_block.append(f"{indent}{ln}")
                    else:
                        new_block.append(f"{ln}")
                    first = False
                        
                    # preserve inner lines but place under proper indentation
                    # new_block.append(f"{indent}{ln}")
            else:
                # keep an empty line for clarity
                # new_block.append(f"{indent}")
                pass
            new_block.append(f"{indent}{quote}")

            edits.append((start, end, new_block))
        else:
            # no docstring: insert before the first body statement
            insert_at = first.lineno - 1
            # compute indentation for the block (same as first statement's leading whitespace)
            leading = re.match(r"^(\s*)", lines[insert_at]).group(1) if insert_at < len(lines) else "    "
            new_block = [f"{leading}\"\"\"", f"{leading}@meta", f"{leading}\"\"\""]
            edits.append((insert_at, insert_at - 1, new_block))

    if not edits:
        return False

    # apply edits from bottom to top so line indices remain valid
    for start, end, new_lines in sorted(edits, key=lambda x: x[0], reverse=True):
        if end >= start:
            lines[start : end + 1] = new_lines
        else:
            lines[start:start] = new_lines

    new_src = "\n".join(lines) + "\n"
    if new_src != src:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new_src)
        return True

    return False


def main(argv: List[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    root = argv[0] if argv else os.getcwd()
    self_path = __file__
    modified = []

    for py in find_python_files(root):
        try:
            changed = insert_meta_into_file(py, self_path)
        except Exception as e:
            # don't fail hard on one file
            print(f"Skipping {py}: {e}")
            changed = False
        if changed:
            modified.append(py)

    if modified:
        print("Modified files:")
        for p in modified:
            print(" -", p)
        return 0
    else:
        print("No changes made.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
