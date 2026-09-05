#!/usr/bin/env python3
"""
Headless smoke test for MathMaster Python sources.

Verifies that the core game modules:
  1. compile without SyntaxError (all .py under src/mathmistress/)
  2. import without syntax errors (via ast.parse, not actual Tk construction)
  3. expose the f-string-bugfix landmarks (tag_str local var)

Does NOT construct any Tk widgets — safe to run on a headless box with
no $DISPLAY.

Run with:
    python3 tests/test_smoke_imports.py
Exits 0 on success, non-zero with diagnostics on failure.
"""

import ast
import glob
import os
import sys


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src", "mathmistress")


def find_syntax_errors(py_files):
    """Return list of (path, error) for any file that fails to parse."""
    out = []
    for path in py_files:
        try:
            ast.parse(open(path, encoding="utf-8").read(), filename=path)
        except SyntaxError as e:
            out.append((path, f"line {e.lineno}: {e.msg}"))
    return out


def check_gameplay_screen_fstring_fix():
    """Confirm the line-1964/1972 nested-f-string bug is fixed."""
    target = os.path.join(SRC_DIR, "gameplay_screen.py")
    src = open(target, encoding="utf-8").read()
    # The nested f-string shape `f"...{f"...}..."` MUST be absent.
    nested_shape = "\"sol_{line_idx}_{char_idx}\"}"  # noqa: SIM222
    if nested_shape in src:
        return ("gameplay_screen.py", "nested f-string still present")
    # The tag_str local-var form must be present (the fix uses it).
    if "{tag_str}" not in src:
        return ("gameplay_screen.py", "tag_str reference missing")
    if "tag_str = f\"sol_{line_idx}_{char_idx}\"" not in src:
        return ("gameplay_screen.py", "tag_str definition missing")
    return None


def main() -> int:
    py_files = glob.glob(os.path.join(SRC_DIR, "*.py"))
    if not py_files:
        print(f"FAIL: no .py files found under {SRC_DIR}", file=sys.stderr)
        return 1

    # 1. Syntax-error sweep.
    errors = find_syntax_errors(py_files)
    if errors:
        for path, msg in errors:
            print(f"  FAIL {os.path.basename(path)}: {msg}")
        print(f"\n{len(errors)} file(s) failed to parse.")
        return 1
    print(f"OK  all {len(py_files)} .py files parse cleanly")

    # 2. f-string-bugfix landmarks.
    fix_err = check_gameplay_screen_fstring_fix()
    if fix_err:
        print(f"  FAIL {fix_err[0]}: {fix_err[1]}")
        return 1
    print("OK  gameplay_screen.py f-string bugfix landmarks present")

    # 3. Welcome-screen chain no longer raises SyntaxError on ast.parse.
    welcome = os.path.join(SRC_DIR, "welcome_screen.py")
    try:
        ast.parse(open(welcome, encoding="utf-8").read(), filename=welcome)
        print("OK  welcome_screen.py parses (transitive import unblocked)")
    except SyntaxError as e:
        print(f"  FAIL welcome_screen.py: line {e.lineno}: {e.msg}", file=sys.stderr)
        return 1

    print(f"\n{len(py_files)} module(s) verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
