"""Generate the Jupyter notebooks students open in JupyterLab or JupyterLite.

Cells come from the marimo notebooks, which are the ground truth. The *prose* comes from the
chapter markdown, pulled in at generation time: the whole chapter, not only the questions, so a
student can work through it without the book open beside them. `notebook_prose.py` converts the
MyST to markdown that every Jupyter front end renders; the marimo notebooks stay prose-free.

    .venv/bin/python scripts/make_jupyter.py            # every chapter that has a notebook
    .venv/bin/python scripts/make_jupyter.py 03.root-finding.md

Solutions are left out. They are generated separately and handed over when the instructors
choose, so `sol_*` cells never reach a student notebook.

`tn23015.py` and `answers/` ship beside the notebooks in the JupyterLite bundle, so the plain
`import tn23015` in the first cell resolves -- `build_jupyter_lite.sh` puts them there.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_notebooks import OUT_DIR, ROOT, chapter_number  # noqa: E402
from notebook_prose import Widget, jupyter_widget, prose  # noqa: E402
from sync_cells import chapter_names, notebook_cells  # noqa: E402

JUPYTER_DIR = ROOT / "jupyter-notebooks"

KERNEL = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12"},
}


def cell(kind: str, ident: str, source: str) -> dict:
    body = {"cell_type": kind, "id": ident, "metadata": {},
            "source": source.rstrip("\n").split("\n")}
    body["source"] = [ln + "\n" for ln in body["source"][:-1]] + body["source"][-1:]
    if kind == "code":
        body |= {"execution_count": None, "outputs": []}
    return body


def build(page: Path) -> dict:
    text = page.read_text(encoding="utf-8")
    number = chapter_number(text)
    bodies = notebook_cells(OUT_DIR / (page.stem + ".py"))
    before, tail = prose(page, "jupyter")

    def prose_cells(name, items):
        for i, item in enumerate(items):
            if isinstance(item, Widget):
                yield cell("code", f"fig_{name}_{i}", jupyter_widget(item))
            else:
                yield cell("markdown", f"md_{name}_{i}", item)

    # The first prose cell is the chapter's `# Title` and its introduction. The setup cell goes
    # straight after the title, where "run the first cell" can find it.
    first = next(iter(before))
    title, *intro = before[first]
    out = [cell("markdown", "title", f"{title}\n\n"
                f"Chapter {number} of the TN23015 book: its explanation and its exercises. "
                f"Run the first cell before anything else, then work down the notebook.")]
    setup = ("import numpy as np\n"
             "import matplotlib.pyplot as plt\n"
             + "".join(ln + "\n" for ln in extra_imports(text))
             + "from tn23015 import "
               "check_answers, given, load_data, md, print, row, show, slider")
    out.append(cell("code", "setup", setup))
    before[first] = intro

    # the same names, in the same order, as the marimo notebook
    for name in chapter_names(text):
        out += prose_cells(name, before.get(name, []))
        if name.startswith("sol_"):
            continue  # released separately
        out.append(cell("code", name, bodies[name]))
    out += prose_cells("end", tail)
    return {"cells": out, "metadata": KERNEL, "nbformat": 4, "nbformat_minor": 5}


def extra_imports(text: str) -> list[str]:
    """The chapter's own imports, minus the ones every notebook gets and minus marimo."""
    head = text.split("ANSWERS = {")[0]
    found = [ln.strip() for ln in head.split("\n") if re.match(r"^  (import|from) ", ln)]
    skip = ("import numpy as np", "import matplotlib.pyplot as plt", "import marimo as mo")
    return [ln for ln in found if ln not in skip]


def main(argv: list[str]) -> int:
    names = argv or [nb.stem + ".md" for nb in sorted(OUT_DIR.glob("[01][0-9].*.py"))]
    JUPYTER_DIR.mkdir(exist_ok=True)
    for name in names:
        page = ROOT / name
        out = JUPYTER_DIR / (page.stem + ".ipynb")
        nb = build(page)
        out.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
        code = sum(c["cell_type"] == "code" for c in nb["cells"])
        print(f"  {out.relative_to(ROOT)}   {code} code + "
              f"{len(nb['cells']) - code} markdown cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
