"""Write the marimo notebooks a student gets: the ground truth minus the solutions.

    .venv/bin/python scripts/make_student_notebooks.py --out _marimo_src

`hide_code=True` is not privacy. A WASM export carries the notebook source inline in
`index.html`, and `marimo edit` shows any cell on request, so a solution that is merely collapsed
is a solution the reader has. Leaving it out is the only thing that actually withholds it.

Everything else is copied through unchanged, including the `head_*` questions, so these notebooks
are the same exercises in the same order as the website and the Jupyter route.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_notebooks import OUT_DIR, ROOT  # noqa: E402


def without_solutions(path: Path) -> tuple[str, int]:
    """The notebook's text with every `sol_*` cell removed, and how many went."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    drop, removed = set(), 0
    for node in ast.parse(text).body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("sol_"):
            continue
        start = min(d.lineno for d in node.decorator_list) - 1
        end = start + 1
        while end < len(lines) and (not lines[end].strip() or lines[end].startswith((" ", "\t"))
                                    or lines[end].startswith(("@app.", "def "))):
            if lines[end].startswith(("@app.", "def ")) and end > start + 1:
                break
            end += 1
        while end > start and not lines[end - 1].strip():
            end -= 1
        drop.update(range(start, end))
        removed += 1
    kept = [ln for i, ln in enumerate(lines) if i not in drop]
    out = "\n".join(kept)
    while "\n\n\n\n" in out:
        out = out.replace("\n\n\n\n", "\n\n\n")
    return out, removed


def main(argv: list[str]) -> int:
    out_dir = Path(argv[argv.index("--out") + 1]) if "--out" in argv else ROOT / "_marimo_src"
    out_dir.mkdir(parents=True, exist_ok=True)
    for nb in sorted(OUT_DIR.glob("[01][0-9].*.py")):
        text, removed = without_solutions(nb)
        (out_dir / nb.name).write_text(text, encoding="utf-8")
        # `sol_2` and `sol_3` are student variables (what `solve_ivp` returned), so the
        # test is for a cell *definition*, not for the substring.
        assert "def sol_" not in text, f"{nb.name}: a solution cell survived"
        print(f"  {nb.name}   {removed} solutions removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
