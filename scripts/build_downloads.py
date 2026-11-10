"""Build the two notebook downloads, for students who want to work on their own computer.

    .venv/bin/python scripts/build_downloads.py

Writes `downloads/tn23015-jupyter-notebooks.zip` and `downloads/tn23015-marimo-notebooks.zip`.
Each unpacks to a folder of the same name holding the eleven chapters, `tn23015.py`, `answers/`,
`data/`, a README and a `requirements.txt`. The module looks for `answers/` and `data/` beside
itself, so the folder works as it unpacks, offline too.

The marimo notebooks are the student versions, with the `sol_*` cells removed, exactly as
`build_marimo_apps.sh` stages them for "open in marimo". The Jupyter notebooks have no solution
cells to begin with.

Not committed: rebuild after the notebooks change. Every file gets the time of the book's last
commit, so the same commit always gives the same zips.
"""

from __future__ import annotations

import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_notebooks import ROOT  # noqa: E402
from make_student_notebooks import without_solutions  # noqa: E402

OUT = ROOT / "downloads"
BOOK_URL = "https://cbl.curve.space/articles/curious-beams-lecture-tn23015-computational-science"
REQUIREMENTS = ["numpy>=2.0", "scipy>=1.14", "matplotlib>=3.10"]

COMMON = """\
## What is in this folder

- {first} … {last}: one notebook per chapter
- `tn23015.py`: the helper module the notebooks import (`show`, `check_answers`, …)
- `answers/`: the reference values the checks compare your results with
- `data/`: the data files that two exercises load

Keep all of these together in this folder, and don't rename them: each notebook looks for
`tn23015.py`, `answers/` and `data/` beside it.

## Setting up (once)

You need Python 3.11 or newer. Open a terminal in this folder and run:

    python -m venv .venv
    source .venv/bin/activate        # on Windows: .venv\\Scripts\\activate
    pip install -r requirements.txt

If you use Anaconda, run this instead: {conda}

With a virtual environment, run the `activate` line again each time you open a new terminal.
"""

FOOTER = """
Everything works offline, except two figures that load from the internet: the ones in
Linear Algebra and PDE I.

Each notebook is a single file on your computer, so make a backup copy now and then.
"""

JUPYTER = """\
# TN23015 Computational Science: Jupyter notebooks

These are the exercises from the course book, as Jupyter notebooks you can run on your own
computer. They are the same exercises with the same checks as the book and its **launch lite**
button.

Book: {book}

{common}
## Working

    jupyter lab

Open a chapter, then run the first cell before anything else.

Jupyter is not reactive, so run the cells in order. After you change an answer, run its check
cell again yourself.

Save often (Ctrl+S, or ⌘S on a Mac). Your work is saved in the `.ipynb` file.
{footer}"""

MARIMO = """\
# TN23015 Computational Science: marimo notebooks

These are the exercises from the course book, as marimo notebooks you can run on your own
computer. They are the same exercises with the same checks as the book and its
**open in marimo** button.

Book: {book}

{common}
## Working

    marimo edit

This opens a page in your browser that lists the notebooks. You can also open one directly, for
example with `marimo edit 01.numerical-differentiation.py`.

The rules are the same as in the book:

- Cells are reactive: when a cell runs, every cell that uses its names runs again.
- Each name is defined in one cell only. Use the name the exercise gives you (`x_2`, `h_2`, …),
  and start scratch variables with an underscore (`_i`, `_fig`, `_ax`).
- Leave each cell's last line, `show(...)`, alone.

Save with Ctrl+S (or ⌘S on a Mac). Your work is saved in the chapter's `.py` file. marimo also
creates a `__marimo__/` folder beside the notebooks, and you can ignore it.
{footer}"""


def commit_time() -> tuple[int, int, int, int, int, int]:
    stamp = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%ct"],
                           capture_output=True, text=True, check=True).stdout.strip()
    return time.gmtime(int(stamp))[:6]


def build(name: str, notebooks: dict[str, str | bytes], module: Path, readme: str,
          extra_requirements: list[str]) -> Path:
    """One zip: `name/` holding the notebooks, the module, answers, data and the README."""
    stamp = commit_time()
    files: dict[str, str | bytes] = dict(notebooks)
    files["tn23015.py"] = module.read_bytes()
    for kind in ("answers", "data"):
        for path in sorted((ROOT / kind).iterdir()):
            if path.is_file():
                files[f"{kind}/{path.name}"] = path.read_bytes()
    files["README.md"] = readme
    files["requirements.txt"] = "\n".join(REQUIREMENTS + extra_requirements) + "\n"

    OUT.mkdir(exist_ok=True)
    target = OUT / f"{name}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in sorted(files):
            info = zipfile.ZipInfo(f"{name}/{rel}", date_time=stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            data = files[rel]
            zf.writestr(info, data.encode("utf-8") if isinstance(data, str) else data)
    print(f"  {target.relative_to(ROOT)}   {len(files)} files, {target.stat().st_size / 1e6:.1f} MB")
    return target


def readme(template: str, names: list[str], conda: str) -> str:
    common = COMMON.format(first=f"`{names[0]}`", last=f"`{names[-1]}`", conda=conda)
    return template.format(book=BOOK_URL, common=common, footer=FOOTER)


def main() -> int:
    # one source for the module: the three copies are kept identical by sync_checker.py
    module = ROOT / "packages" / "tn23015.py"

    ipynb = {p.name: p.read_bytes() for p in sorted((ROOT / "jupyter-notebooks").glob("[01][0-9].*.ipynb"))}
    build("tn23015-jupyter-notebooks", ipynb, module,
          readme(JUPYTER, list(ipynb), "`conda install numpy scipy matplotlib jupyterlab`"),
          ["jupyterlab"])

    marimo = {}
    for nb in sorted((ROOT / "marimo-notebooks").glob("[01][0-9].*.py")):
        text, _ = without_solutions(nb)
        assert "def sol_" not in text, f"{nb.name}: a solution cell survived"
        marimo[nb.name] = text
    build("tn23015-marimo-notebooks", marimo, module,
          readme(MARIMO, list(marimo),
                 "`conda install -c conda-forge numpy scipy matplotlib marimo`"),
          ["marimo>=0.23.16"])

    assert len(ipynb) == len(marimo) == 11, (len(ipynb), len(marimo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
