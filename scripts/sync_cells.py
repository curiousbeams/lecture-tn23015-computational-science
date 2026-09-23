"""Keep the marimo notebooks and the chapters in step.

Two things are authored, in different places, and this carries each to the other:

    code       notebook  ->  markdown     the bodies of the `{marimo}` blocks, and nothing else
    questions  markdown  ->  notebook     the `head_*` cells, from the `{exercise-start}` prose

Nothing is edited in two places, so there is never a merge to resolve -- and `--check` fails if
either side has been changed without the other being brought along. Prose, directive options,
block order and the page header are hand-edited and this script has no opinion about them.

    .venv/bin/python scripts/sync_cells.py            # write every chapter that has a notebook
    .venv/bin/python scripts/sync_cells.py --check    # verify only, non-zero if they disagree

Cells are matched **by name**, never by position: `ex_3_01` in the notebook goes to the block the
chapter calls `ex_3_01`. Matching by position would pair the wrong cells the first time either
side gained or lost one, and would do it silently.

Cells whose name the markdown does not have are reported rather than inserted. Where a new
exercise belongs in the prose is an editorial decision, and guessing it would be worse than
saying so. Two prefixes have no block by design: `head_*`, because the page renders the question
from its own prose, and `sol_*`, because `strip_solutions.py` took the solutions off the website
and `make_solutions.py` generates them into `solutions/` instead.

Running it is idempotent: the extractor indents each body to sit inside its `def`, and this
undoes exactly that, so a notebook extracted and synced back leaves `git diff` empty.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_notebooks import (  # noqa: E402
    FENCE, OUT_DIR, ROOT, cells, exercise_numbers, exercise_prose, heading_body, indent,
    to_markdown, unique,
)


def notebook_cells(path: Path) -> dict[str, str]:
    """{cell name: body}, dedented back to column zero.

    Read with `ast` rather than by regex because `marimo edit` rewrites the file when it saves:
    it may add the dependency signature (`def ex_3_01(np, plt):`) and a trailing `return`. Both
    are marimo's bookkeeping, not the reader's code, so neither survives the trip back.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    out = {}
    for node in ast.parse(text).body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if not any("cell" in ast.dump(d) for d in node.decorator_list):
            continue
        # The block is taken by text, not from the AST: a cell almost always opens with a comment
        # and comments are not nodes, so `body[0].lineno` would start below the first line the
        # reader sees. Walk past the signature (which marimo may wrap over several lines), then
        # to the next line at column zero.
        i, depth = node.lineno - 1, 0
        while True:
            depth += lines[i].count("(") - lines[i].count(")")
            if depth == 0 and lines[i].rstrip().endswith(":"):
                break
            i += 1
        start = i + 1
        end = start
        while end < len(lines) and (not lines[end].strip() or lines[end].startswith((" ", "\t"))):
            end += 1
        if isinstance(node.body[-1], ast.Return):
            end = min(end, node.body[-1].lineno - 1)  # marimo's bookkeeping, not the reader's code
        chunk = lines[start:end]
        while chunk and not chunk[-1].strip():
            chunk.pop()
        out[node.name] = "\n".join(ln[4:] if ln.startswith("    ") else ln for ln in chunk)
    return out


def refresh_headings(nb: Path, page_text: str) -> str:
    """The notebook with its `head_*` cells rebuilt from the chapter's exercise prose.

    Code travels notebook -> markdown; the questions travel markdown -> notebook. Neither is
    edited in two places, and `--check` fails if either side has been.
    """
    numbers, prose = exercise_numbers(page_text), exercise_prose(page_text)
    text = nb.read_text(encoding="utf-8")
    lines = text.split("\n")
    for name, start, end in reversed(spans(text)):
        if not name.startswith("head_"):
            continue
        key = name[5:]
        if key not in numbers:
            continue
        body = heading_body(key, numbers[key], to_markdown(prose.get(key, ""), numbers))
        lines[start:end] = indent(body).split("\n")
    return "\n".join(lines)


def spans(text: str) -> list[tuple[str, int, int]]:
    """(cell name, first body line, line after the body) for every `@app.cell` in the file."""
    lines = text.split("\n")
    out = []
    for node in ast.parse(text).body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if not any("cell" in ast.dump(d) for d in node.decorator_list):
            continue
        i, depth = node.lineno - 1, 0
        while True:
            depth += lines[i].count("(") - lines[i].count(")")
            if depth == 0 and lines[i].rstrip().endswith(":"):
                break
            i += 1
        start = end = i + 1
        while end < len(lines) and (not lines[end].strip() or lines[end].startswith((" ", "\t"))):
            end += 1
        if isinstance(node.body[-1], ast.Return):
            end = min(end, node.body[-1].lineno - 1)
        while end > start and not lines[end - 1].strip():
            end -= 1
        out.append((node.name, start, end))
    return out


def chapter_names(text: str) -> list[str]:
    """The name of each `{marimo}` block, in page order -- the extractor's rules, reapplied."""
    seen: set[str] = set()
    return [unique(f"{kind}_{key}", seen) for (kind, key), _, _ in cells(text)]


def rewrite(path: Path, bodies: dict[str, str]) -> tuple[str, list[str]]:
    """The page with each block replaced by its notebook cell. Returns (text, unplaced names)."""
    text = path.read_text(encoding="utf-8")
    names = chapter_names(text)
    lines = text.split("\n")
    out, i, n = [], 0, 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].strip() != FENCE:
            i += 1
            continue
        i += 1
        while i < len(lines) and lines[i].startswith(":"):
            out.append(lines[i])
            i += 1
        # The blank line that separates the options from the code is the page's, not the cell's;
        # the notebook stores bodies stripped, so it has to be carried over rather than guessed.
        while i < len(lines) and not lines[i].strip():
            out.append(lines[i])
            i += 1
        start = i
        while i < len(lines) and lines[i].strip() != "```":
            i += 1
        trail = 0
        while start + trail < i and not lines[i - 1 - trail].strip():
            trail += 1
        name = names[n]
        n += 1
        out.extend(bodies[name].split("\n") if name in bodies else lines[start:i - trail])
        out.extend([""] * trail)
    placed = set(names)
    # `head_*` is notebook-only navigation and `sol_*` was deliberately taken off the website by
    # `strip_solutions.py`; neither has a block here, and neither is a problem.
    unplaced = [k for k in bodies if k not in placed and not k.startswith(("head_", "sol_"))]
    return "\n".join(out), unplaced


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    stale, problems = [], []
    for nb in sorted(OUT_DIR.glob("[01][0-9].*.py")):
        page = ROOT / (nb.stem + ".md")
        if not page.exists():
            problems.append(f"{nb.name}: no chapter {page.name}")
            continue
        page_text = page.read_text(encoding="utf-8")
        headings = refresh_headings(nb, page_text)
        if headings != nb.read_text(encoding="utf-8"):
            stale.append(nb.name)
            if not check_only:
                nb.write_text(headings, encoding="utf-8")

        bodies = notebook_cells(nb)
        want, unplaced = rewrite(page, bodies)
        for name in unplaced:
            problems.append(f"{nb.name}: `{name}` has no block in {page.name}; add one by hand")
        if want == page_text:
            continue
        stale.append(page.name)
        if not check_only:
            page.write_text(want, encoding="utf-8")
    for line in problems:
        print("  " + line)
    verb = "out of step" if check_only else "synced"
    print(f"{len(stale)} file(s) {verb}" + (f": {', '.join(stale)}" if stale else ""))
    return 1 if problems or (check_only and stale) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
