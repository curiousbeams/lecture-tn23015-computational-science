"""Generate the solutions notebooks, which are never on the website.

    .venv/bin/python scripts/make_solutions.py

Writes `solutions/NN.<slug>.py` (marimo) and `solutions/NN.<slug>.ipynb` (Jupyter) from the
ground-truth notebooks: the setup block, the exercise headings, the read-only demonstrations, and
the `sol_*` cells. The stubs and the answer checks are dropped -- a solutions notebook is for
reading and running, not for filling in.

**The demonstrations have to come too.** Solutions are not self-contained: measured across the
eleven chapters, they read exactly three things from outside themselves, all defined in `demo_*`
cells -- `s = np.fft.fftshift` in Fourier Transforms I, the `X`/`Y` meshgrid in II, and
`my_dst`/`my_idst` in PDEs II. Nothing is read from an `ex_*` cell, because every solution works
in its own `_solN`-suffixed names.

**Be honest about what this achieves.** The repository is public and the solutions are in its
history, so generating them here takes them off the student's path; it does not make them secret.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_notebooks import OUT_DIR, ROOT, exercise_numbers, exercise_prose, to_markdown  # noqa: E402
from make_jupyter import KERNEL, cell, extra_imports  # noqa: E402
from sync_cells import notebook_cells, spans  # noqa: E402

SOLUTIONS = ROOT / "solutions"
DROP = ("ex_", "check_")

# names the setup block and the runtime provide
GIVEN = {"check_answers", "given", "load_data", "md", "print", "row", "show", "slider",
         "np", "plt", "mo", "solve_ivp", "find_peaks", "time", "colors", "dst", "idst",
         "array", "empty"}


def _bound(src):
    out = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            out.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            out.add(node.name)
        elif isinstance(node, ast.arg):
            out.add(node.arg)
    return out


def _free(src):
    loads = {n.id for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    return loads - _bound(src) - GIVEN - set(dir(__builtins__))


def usable_demos(bodies):
    """{demo cell: names to stub out} for the demonstrations worth carrying over.

    Most demonstrations exist to display what the *reader* produced -- `if given(phi):` and a plot
    of it -- so with the stubs gone they are a NameError, and they are dropped. A few define
    helpers the solutions need: `s = np.fft.fftshift`, `my_dst`/`my_idst`, the FT2 meshgrid.

    FT1's is both at once -- it defines `s` and then plots the reader's `f` and `yt` behind a
    guard. Dropping it loses `s`; keeping it is a NameError on a name that is only ever read
    inside `if given(f, yt):`. So it is kept with those names bound to None, which is exactly what
    the guard is for: it stays closed and the cell defines its helper and displays nothing.
    """
    wanted = {n for name, src in bodies.items() if name.startswith("sol_") for n in _free(src)}
    have, keep = set(GIVEN), {}
    for name, src in bodies.items():
        if not name.startswith("demo_"):
            continue
        missing = _free(src) - have
        if not missing:
            keep[name] = ()
        elif _bound(src) & wanted:
            keep[name] = tuple(sorted(missing))
        else:
            continue
        have |= _bound(src)
    return keep


def stub_out(src: str, names: tuple[str, ...]) -> str:
    """The cell with the reader's unfilled names bound to None, so its guard stays closed."""
    if not names:
        return src
    return (f"# The exercises are not in this notebook, so what they would define is blank and\n"
            f"# the guard below stays closed.\n{' = '.join(names)} = None\n\n{src}")


def marimo_source(nb: Path) -> tuple[str, int]:
    """The notebook with every stub and check removed, and how many solutions it keeps."""
    text = nb.read_text(encoding="utf-8")
    lines = text.split("\n")
    keep_demos = usable_demos(notebook_cells(nb))
    drop: set[int] = set()
    for node in ast.parse(text).body:
        if not isinstance(node, ast.FunctionDef):
            continue
        doomed = node.name.startswith(DROP) or (
            node.name.startswith("demo_") and node.name not in keep_demos)
        if not doomed:
            continue
        start = min(d.lineno for d in node.decorator_list) - 1
        end = next((s for n, s, _ in spans(text) if n == node.name), start)
        _, _, end = next(s for s in spans(text) if s[0] == node.name)
        while end < len(lines) and not lines[end].strip():
            end += 1
        drop.update(range(start, end))
    lines = list(lines)
    for name, missing in keep_demos.items():
        if not missing:
            continue
        _, body_start, _ = next(s for s in spans(text) if s[0] == name)
        lines[body_start] = ("    # The exercises are not in this notebook, so what they would "
                             "define is blank\n    # and the guard below stays closed.\n    "
                             + " = ".join(missing) + " = None\n\n" + lines[body_start])
    kept = "\n".join(ln for i, ln in enumerate(lines) if i not in drop)
    while "\n\n\n\n" in kept:
        kept = kept.replace("\n\n\n\n", "\n\n\n")
    return kept, sum(1 for n, _, _ in spans(text) if n.startswith("sol_"))


def jupyter(nb: Path, page: Path) -> dict:
    text = page.read_text(encoding="utf-8")
    title = text.split("title:", 1)[1].split("\n", 1)[0].strip()
    numbers, prose = exercise_numbers(text), exercise_prose(text)
    bodies = notebook_cells(nb)
    keep_demos = usable_demos(bodies)

    cells = [cell("markdown", "title", f"# {title} — solutions\n\n"
                  "Reference solutions for the exercises in this chapter. Every variable is "
                  "suffixed `_sol1`, `_sol2` and so on, so running these never overwrites your "
                  "own work in the exercise notebook.")]
    cells.append(cell("code", "setup",
                      "import numpy as np\nimport matplotlib.pyplot as plt\n"
                      + "".join(f"{ln}\n" for ln in extra_imports(text))
                      + "from tn23015 import "
                        "check_answers, given, load_data, md, print, row, show, slider"))
    for name, _, _ in spans(nb.read_text(encoding="utf-8")):
        if name.startswith("head_"):
            key = name[5:]
            if key in numbers:
                question = to_markdown(prose.get(key, ""), numbers)
                cells.append(cell("markdown", name, f"## Exercise {numbers[key]}"
                                  + (f"\n\n{question}" if question else "")))
        elif name.startswith("sol_") or name in keep_demos:
            cells.append(cell("code", name, stub_out(bodies[name], keep_demos.get(name, ()))))
    return {"cells": cells, "metadata": KERNEL, "nbformat": 4, "nbformat_minor": 5}


def main(argv: list[str]) -> int:
    SOLUTIONS.mkdir(exist_ok=True)
    total = 0
    for nb in sorted(OUT_DIR.glob("[01][0-9].*.py")):
        page = ROOT / (nb.stem + ".md")
        source, kept = marimo_source(nb)
        assert "def ex_" not in source and "def check_" not in source, nb.name
        (SOLUTIONS / nb.name).write_text(source, encoding="utf-8")
        (SOLUTIONS / (nb.stem + ".ipynb")).write_text(
            json.dumps(jupyter(nb, page), indent=1) + "\n", encoding="utf-8")
        total += kept
        print(f"  solutions/{nb.stem}   {kept} solutions")
    print(f"{total} solutions across {len(list(SOLUTIONS.glob('[01][0-9].*.py')))} chapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
