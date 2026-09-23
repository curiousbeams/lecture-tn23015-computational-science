"""Remove the solution dropdowns from the chapter markdown.

    .venv/bin/python scripts/strip_solutions.py
    .venv/bin/python scripts/strip_solutions.py --check

Takes out each `:::{solution-start} … :::{solution-end}` region and the `{marimo}` block inside
it. The solutions themselves are not lost: they are the ground truth's `sol_*` cells, and
`scripts/make_solutions.py` generates `solutions/` from them for release when the instructors
choose.

This is one-way. `sync_cells.py` writes code from the notebooks into the blocks the markdown
*has*, so once a solution block is gone it stays gone -- and `sol_*` cells are exempt from its
"no block for this cell" complaint for exactly that reason.

**Be honest about what it achieves.** The repository is public and every solution is in its git
history. This takes them off the student's path; it does not make them secret.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = ":::{solution-start}"
END = ":::{solution-end}"


def strip(text: str) -> tuple[str, int]:
    lines, out, i, removed = text.split("\n"), [], 0, 0
    while i < len(lines):
        if not lines[i].startswith(START):
            out.append(lines[i])
            i += 1
            continue
        while i < len(lines) and not lines[i].startswith(END):
            i += 1
        i += 1                                   # the `:::{solution-end}` line
        while i < len(lines) and lines[i].strip() == ":::":
            i += 1                               # its closing fence
        while i < len(lines) and not lines[i].strip():
            i += 1                               # and the blank line after it
        while out and not out[-1].strip():
            out.pop()                            # plus the one before, so nothing doubles up
        out.append("")
        removed += 1
    return "\n".join(out), removed


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    total, touched = 0, []
    for path in sorted(ROOT.glob("[01][0-9].*.md")):
        if path.name.startswith("00."):
            continue
        text = path.read_text(encoding="utf-8")
        new, removed = strip(text)
        if not removed:
            continue
        total += removed
        touched.append(f"{path.name} ({removed})")
        if not check_only:
            path.write_text(new, encoding="utf-8")
    verb = "still present in" if check_only else "removed from"
    print(f"{total} solution block(s) {verb} {len(touched)} chapter(s)")
    for name in touched:
        print(f"  {name}")
    return 1 if check_only and total else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
