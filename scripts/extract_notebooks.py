"""Extract a chapter's exercises into a real marimo notebook.

The notebooks are the ground truth for the *exercises*; the prose stays in the markdown and is
never touched by any generator. Run once per chapter to create the notebook, after which the
markdown's code blocks are generated from it by `sync_cells.py`.

    .venv/bin/python scripts/extract_notebooks.py 01.numerical-differentiation.md
    .venv/bin/python scripts/extract_notebooks.py --all

**Cell names are the join key.** Every cell gets one, and the prefix says what it is:

    setup       the imports, as marimo's `with app.setup:` block
    head_3_01   a markdown heading naming the exercise -- notebook only, never written back
    ex_3_01     the stub the reader fills in
    check_3_01  the answer check, matched to its exercise by the `key=` argument rather than by
                position: check cells sit *outside* the `{exercise-start}` region
    sol_3_01    the reference solution
    demo_07     a read-only demonstration that belongs to no exercise

`sync_cells.py` matches on those names, so a cell can be moved, and blocks can be added or
removed, without anything silently pairing up wrongly.

The body of every cell is copied verbatim (indented by four spaces to sit inside the function,
which `sync_cells.py` undoes), so the round trip is exact.

What the notebook does *not* carry is the runtime: the markdown pages embed a copy of it in their
header because a browser has nothing to import from, while the notebook imports `tn23015`.
`sync_checker.py` still owns the header.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "marimo-notebooks"

# The imports each chapter's header opens with, beyond the three every chapter has.
FENCE = "```{marimo} python"
RUNTIME = ("from tn23015 import check_answers, given, load_data, md, print, row, show, slider")
BASE_IMPORTS = ["import marimo as mo", "import numpy as np", "import matplotlib.pyplot as plt"]

# Only the stubs show their code. A check cell is machinery and a solution is a spoiler; both
# still *run*, and marimo will reveal either on request, but opening the notebook should look
# like the exercises and nothing else.
HIDDEN = "@app.cell(hide_code=True)"


RAW = ("https://raw.githubusercontent.com/curiousbeams/"
       "lecture-tn23015-computational-science/main/")


def exercise_prose(text: str) -> dict[str, str]:
    """{exercise key: the question}, from `{exercise-start}` to the first code block.

    The prose is *authored in the markdown* and copied into the notebooks from there. It travels
    the opposite way to the code, which is authored in the notebooks -- so nothing is edited in
    two places, and `sync_cells.py --check` fails if either side has drifted.
    """
    out, lines, i = {}, text.split("\n"), 0
    while i < len(lines):
        if lines[i].strip().startswith(":::{exercise-start}"):
            i += 1
            key = None
            while i < len(lines) and lines[i].strip() != ":::":
                if lines[i].strip().startswith(":label: ex_"):
                    key = lines[i].split()[1][3:]
                i += 1
            body, i = [], i + 1
            while i < len(lines) and not lines[i].startswith(FENCE) \
                    and not lines[i].strip().startswith(":::{exercise-end}"):
                body.append(lines[i])
                i += 1
            if key:
                out[key] = "\n".join(body).strip("\n")
        i += 1
    return out


def exercise_numbers(text: str) -> dict[str, str]:
    """{exercise key: the number the site prints}, e.g. `5_01` -> `3.1`."""
    number, out = chapter_number(text), {}
    for (kind, key), _, _ in cells(text):
        if kind == "ex" and key not in out:
            out[key] = f"{number}.{len(out) + 1}"
    return out


def to_markdown(text: str, numbers: dict[str, str]) -> str:
    """MyST that a plain markdown renderer cannot handle, turned into something it can."""
    # `[](#ex_3_02)` is a MyST cross-reference; neither marimo nor a notebook has a resolver, so
    # it becomes the number the reader sees on the website and in these notebooks' own headings.
    text = re.sub(r"\[\]\(#ex_([0-9a-z_]+)\)",
                  lambda m: f"Exercise {numbers.get(m.group(1), m.group(1))}", text)
    text = re.sub(r"\]\(wiki:([^)]+)\)", r"](https://en.wikipedia.org/wiki/\1)", text)
    # figures come from the public repository rather than being shipped beside the notebook
    text = re.sub(r"^:::\{figure\}\s*\./([^\n]+)\n(?::[^\n]*\n)*:::$",
                  lambda m: f"![]({RAW}{m.group(1)})", text, flags=re.M)
    text = re.sub(r"^:::\{(hint|note|tip|important|warning)\}\n(.*?)\n:::$",
                  lambda m: "> **" + m.group(1).title() + "** — "
                            + m.group(2).replace("\n", "\n> "),
                  text, flags=re.M | re.S)
    return text


def heading_body(key: str, number: str, prose: str) -> str:
    """The body of a `head_*` cell: `mo.md` of the exercise's number and question.

    marimo dedents the markdown it is given, so the string can sit indented inside the function.
    It is raw because the questions are full of LaTeX, and `\\lambda` in a cooked string is both a
    SyntaxWarning and the wrong character.
    """
    text = f"## Exercise {number}" + (f"\n\n{prose}" if prose else "")
    assert '"""' not in text, f"{key}: the question contains a triple quote"
    body = "\n".join(("    " + ln) if ln.strip() else "" for ln in text.split("\n"))
    return f'mo.md(\n    r"""\n{body}\n    """\n)'


def chapter_number(text: str) -> str:
    """The number the site prints in front of an exercise, from `enumerator: 1.%s`."""
    m = re.search(r"^\s*enumerator:\s*(\d+)\.%s\s*$", text, re.M)
    return m.group(1) if m else "?"


def header_imports(text: str) -> list[str]:
    """The chapter's own imports, minus the three in BASE_IMPORTS and marimo itself."""
    head = text.split("ANSWERS = {")[0]
    found = [ln.strip() for ln in head.split("\n") if re.match(r"^  (import|from) ", ln)]
    return [ln for ln in found if ln not in BASE_IMPORTS]


def cells(text: str):
    """Walk the page, yielding (name_hint, body) for every `{marimo}` block.

    name_hint is ("sol"|"ex"|"check"|"demo", key) -- the key comes from the exercise label, or
    for a check cell from its own `key=` argument, because check cells sit outside the exercise.
    """
    lines = text.split("\n")
    i, exercise, in_solution, demo, order = 0, None, None, 0, 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith(":::{exercise-start}"):
            exercise = "?"
        elif s.startswith(":label: ex_") and exercise == "?":
            exercise = s.split()[1][3:]  # ex_3_01 -> 3_01
        elif s.startswith(":::{exercise-end}"):
            exercise = None
        elif s.startswith(":::{solution-start}"):
            tail = s.split()[-1]
            in_solution = tail[3:] if tail.startswith("ex_") else "?"
        elif s.startswith(":::{solution-end}"):
            in_solution = None
        elif s == FENCE:
            i += 1
            while i < len(lines) and lines[i].startswith(":"):
                i += 1
            body = []
            while i < len(lines) and lines[i].strip() != "```":
                body.append(lines[i])
                i += 1
            src = "\n".join(body).strip("\n")
            order += 1
            key = re.search(r'key="answer_([0-9a-z_]+)"', src)
            if in_solution:
                yield ("sol", in_solution), src, order
            elif src.startswith("check_answers(") and key:
                yield ("check", key.group(1)), src, order
            elif exercise:
                yield ("ex", exercise), src, order
            else:
                demo += 1
                yield ("demo", f"{demo:02d}"), src, order
        i += 1


def unique(name: str, seen: set[str]) -> str:
    """`ex_3_01`, then `ex_3_01b`, `ex_3_01c` -- exercises with more than one cell of a kind."""
    if name not in seen:
        seen.add(name)
        return name
    for suffix in "bcdefghijk":
        if name + suffix not in seen:
            seen.add(name + suffix)
            return name + suffix
    raise AssertionError(f"too many cells named {name}")


def indent(src: str) -> str:
    return "\n".join(("    " + ln) if ln.strip() else "" for ln in src.split("\n"))


def build(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    title = re.search(r"^title:\s*(.+)$", text, re.M).group(1).strip()

    out = ['import marimo', "", 'app = marimo.App(width="medium")', "", "with app.setup:"]
    for line in BASE_IMPORTS + header_imports(text) + [RUNTIME]:
        out.append("    " + line)
    out.append("")

    seen: set[str] = set()
    numbered = exercise_numbers(text)
    prose = exercise_prose(text)
    for (kind, key), src, _ in cells(text):
        if kind == "ex" and f"head_{key}" not in seen:
            head = unique(f"head_{key}", seen)
            body = heading_body(key, numbered[key], to_markdown(prose.get(key, ""), numbered))
            out += ["", "@app.cell(hide_code=True)", f"def {head}():", indent(body), ""]
        name = unique(f"{kind}_{key}", seen)
        out += ["", HIDDEN if kind in ("check", "sol") else "@app.cell", f"def {name}():",
                indent(src), ""]

    out += ["", 'if __name__ == "__main__":', "    app.run()", ""]
    return re.sub(r"\n{3,}", "\n\n\n", "\n".join(out)).lstrip("\n"), title


def main(argv: list[str]) -> int:
    names = argv
    if "--all" in argv:  # the index and the about page carry no exercises
        names = sorted(p.name for p in ROOT.glob("[01][0-9].*.md")
                       if not p.name.startswith("00."))
    if not names:
        print(__doc__.split("\n\n")[1])
        return 2
    OUT_DIR.mkdir(exist_ok=True)
    for name in names:
        path = ROOT / name
        source, title = build(path)
        out = OUT_DIR / (path.stem + ".py")
        out.write_text(source, encoding="utf-8")
        n = source.count("@app.cell")
        print(f"  {out.relative_to(ROOT)}   {n} cells   ({title})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
