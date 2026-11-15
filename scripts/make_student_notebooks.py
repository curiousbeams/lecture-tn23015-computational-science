"""Write the marimo notebooks a student gets: the ground truth minus the solutions, plus the prose.

    .venv/bin/python scripts/make_student_notebooks.py --out _marimo_src

`hide_code=True` is not privacy. A WASM export carries the notebook source inline in
`index.html`, and `marimo edit` shows any cell on request, so a solution that is merely collapsed
is a solution the reader has. Leaving it out is the only thing that actually withholds it.

The chapter's explanation goes in from the markdown, as hidden markdown cells in front of the cells
they introduce (`notebook_prose.py`). The `head_*` questions are dropped, because the prose already
carries each exercise's heading and question. Every code cell is copied through unchanged, so these
are the same exercises in the same order as the website and the Jupyter route.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_notebooks import OUT_DIR, ROOT  # noqa: E402
from notebook_prose import Widget, marimo_markdown, marimo_widget, prose  # noqa: E402


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


# Under the title of each browser notebook, where the student is when the question comes up. Only
# the browser build gets it: in the marimo zip, saving is just Ctrl+S, and the link would go nowhere.
SAVING = """/// details | Saving your work
    type: tip

Save often (Ctrl+S, or ⌘S on a Mac). Each save keeps your work in this page's address, so reloading,
reopening the tab or a bookmark brings it back. The book's **open in marimo** button always opens a
fresh copy, so bookmark this page once you have saved.

To keep a file, choose Download → Download notebook source from the menu. To carry on from one,
[continue a saved notebook](../continue.html?chapter=<slug>).
///"""


def with_prose(text: str, page: Path, web: bool = False) -> tuple[str, int]:
    """The notebook with the chapter's prose cells in place of its `head_*` cells.

    Each prose cell goes in front of the code cell that follows it on the page, matched by name.
    Any prose whose cell is not in the notebook is an error rather than being dropped.
    """
    before, tail = prose(page, "marimo")
    if web:
        first = next(iter(before))
        before[first][0] += "\n\n" + SAVING.replace("<slug>", page.stem)
    lines = text.split("\n")
    blocks = [(node.name, min(d.lineno for d in node.decorator_list) - 1, node.end_lineno)
              for node in ast.parse(text).body
              if isinstance(node, ast.FunctionDef) and node.decorator_list]
    missing = set(before) - {name for name, _, _ in blocks}
    assert not missing, f"{page.name}: prose for cells the notebook does not have: {missing}"

    def rendered(cells):
        out = []
        for cell in cells:
            out += (marimo_widget(cell) if isinstance(cell, Widget) else marimo_markdown(cell)).split("\n")
            out += ["", ""]
        return out

    end = next(i for i, ln in enumerate(lines) if ln.startswith('if __name__ == "__main__":'))
    lines[end:end] = rendered(tail)
    added = len(tail)
    for name, start, stop in reversed(blocks):     # bottom up, so earlier line numbers hold
        if name.startswith("head_"):
            del lines[start:stop]
        if name in before:
            lines[start:start] = rendered(before[name])
            added += len(before[name])
    out = "\n".join(lines)
    while "\n\n\n\n" in out:
        out = out.replace("\n\n\n\n", "\n\n\n")
    assert "def head_" not in out, f"{page.name}: a question cell survived"
    return out, added


def student_notebook(nb: Path, web: bool = False) -> str:
    """What a student opens: no solutions, and the chapter's explanation around the exercises.

    `web` is for the browser build ("open in marimo"), which also says how saving works there.
    """
    text, _ = without_solutions(nb)
    # `sol_2` and `sol_3` are student variables (what `solve_ivp` returned), so the test is for a
    # cell *definition*, not for the substring.
    assert "def sol_" not in text, f"{nb.name}: a solution cell survived"
    text, _ = with_prose(text, ROOT / (nb.stem + ".md"), web)
    compile(text, nb.name, "exec")
    return text


def main(argv: list[str]) -> int:
    out_dir = Path(argv[argv.index("--out") + 1]) if "--out" in argv else ROOT / "_marimo_src"
    out_dir.mkdir(parents=True, exist_ok=True)
    for nb in sorted(OUT_DIR.glob("[01][0-9].*.py")):
        text = student_notebook(nb, web="--web" in argv)
        (out_dir / nb.name).write_text(text, encoding="utf-8")
        print(f"  {nb.name}   {text.count('@app.cell')} cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
