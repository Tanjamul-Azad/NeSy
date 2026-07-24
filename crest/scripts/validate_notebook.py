"""Syntax-check every code cell in the Kaggle notebook before pushing.

Motivation: a Kaggle run costs GPU quota and ~10 minutes of model loading
before it ever reaches the experiment cell. A run was already lost to a
plain SyntaxError (a literal newline inside a Python string literal, which
the notebook JSON happily stored). Catching that here takes milliseconds.

IPython magics (`!cmd`, `%cd`) are not valid Python, so lines starting with
those are stripped before parsing rather than treated as failures.

Usage: python scripts/validate_notebook.py [notebook.ipynb ...]
Exits non-zero if any code cell fails to parse.
"""

import ast
import json
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent / "kaggle_kernel" / "crest_kaggle.ipynb"


def strip_magics(src: str) -> str:
    keep = []
    for line in src.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("!") or stripped.startswith("%"):
            keep.append("pass  # magic")
        else:
            keep.append(line)
    return "\n".join(keep)


def validate(path: Path) -> int:
    nb = json.loads(path.read_text(encoding="utf-8"))
    failures = 0
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = strip_magics("".join(cell["source"]))
        try:
            ast.parse(src)
        except SyntaxError as e:
            failures += 1
            print(f"FAIL {path.name} cell {i}: {e}")
            for n, line in enumerate(src.split("\n"), 1):
                marker = " <<<" if n == e.lineno else ""
                print(f"    {n:3d}| {line}{marker}")
    if failures:
        print(f"\n{failures} code cell(s) failed to parse in {path.name}")
    else:
        print(f"OK  {path.name}: all code cells parse")
    return failures


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]] or [DEFAULT]
    sys.exit(1 if sum(validate(p) for p in paths) else 0)
