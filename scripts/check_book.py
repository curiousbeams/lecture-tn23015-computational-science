"""Three checks on the built chapters that `validate_page.py` does not cover.

`validate_page.py` answers "does every cell run?" and "does any global have two owners?".
These answer three questions about what a *reader* sees, each of which caught a real bug that
nothing else would have:

    runs      every cell executes, including the ones validate_page forgives as "expected"
              stub failures -- an unfilled exercise must sit quietly, not throw
    checks    no answer check renders a verdict before the reader has typed anything. Only
              amber ("waiting") is correct on a fresh page; green or red means the exercise is
              grading scaffolding, which is how ODE1 came to check uninitialised memory
    outputs   no solution displays nothing. Solutions are executable *because* their output is
              the teaching; one that renders an empty cell is a solution the reader cannot use

Usage:
    .venv/bin/python scripts/check_book.py            # all three, over every chapter
    .venv/bin/python scripts/check_book.py runs -v    # one check, showing the offending source

Exits non-zero if anything fails, so it can gate a commit or a deploy.
"""

from __future__ import annotations

import glob
import re
import sys
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_page as V  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

CHAPTERS = sorted(glob.glob("0*.md") + glob.glob("1*.md"))
BUDGET = 300  # seconds per cell; the PDE relaxation loops are genuinely slow


def page_namespace(path: Path) -> dict:
    """A fresh namespace with the page's header (imports, answer bank, runtime) executed."""
    ns = {"np": np, "plt": plt, "mo": V.FakeMo()}
    src = V.page_header_source(path)
    if src:
        exec(src, ns)
        ns["mo"] = V.FakeMo()  # the stub reads run buttons as pressed and never stops the sweep
    return ns


def sweep(path: Path):
    """Run a page top to bottom, yielding (index, kind, source, result-or-exception)."""
    ns = page_namespace(path)
    for idx, (src, in_sol) in enumerate(V.extract_cells_tagged(path)):
        kind = V.classify(src, in_sol)
        result = exc = None
        try:
            with V.time_limit(BUDGET):
                if kind == "check":
                    result = eval(src.strip(), ns)
                else:
                    exec(src, ns)
        except V.StopSignal:
            pass
        except BaseException:  # noqa: BLE001 - reporting, not handling
            exc = traceback.format_exc().strip().split("\n")[-1]
        finally:
            plt.close("all")
        yield idx, kind, src, result, exc


def check_runs(verbose: bool) -> int:
    bad = 0
    for name in CHAPTERS:
        for idx, kind, src, _, exc in sweep(V.ROOT / name):
            if exc is None:
                continue
            # a check cell whose answers are undefined is the reader not having started yet;
            # marimo never runs a descendant of a failed cell, so this never reaches them
            if kind == "check" and "NameError" in exc and "answer_" in exc:
                continue
            bad += 1
            print(f"  {name} cell {idx} [{kind}] {exc}")
            if verbose:
                for line in src.strip().split("\n"):
                    print("      " + line[:110])
    print(f"runs:    {bad} failing cells")
    return bad


def check_checks(verbose: bool) -> int:
    bad = 0
    for name in CHAPTERS:
        ex = 0
        for idx, kind, src, result, exc in sweep(V.ROOT / name):
            if kind != "check":
                continue
            ex += 1
            text = f"RAISED {exc}" if exc else str(result)
            if text.startswith("[warn]"):
                continue  # correct: waiting for the reader
            verdict = "GREEN" if "[success]" in text else ("RED" if "[danger]" in text else text[:40])
            bad += 1
            print(f"  {name} check {ex} (cell {idx}): {verdict}")
            if verbose:
                print("      " + src.strip()[:110])
    print(f"checks:  {bad} verdicts rendered before the reader typed anything")
    return bad


def check_outputs(verbose: bool) -> int:
    bad = 0
    for name in CHAPTERS:
        for idx, kind, src, _, _ in sweep(V.ROOT / name):
            if kind != "solution":
                continue
            displays = bool(re.search(r"^show\([^)]", src, re.M))
            prints = "print(" in src
            if displays or prints:
                continue
            bad += 1
            print(f"  {name} cell {idx}: solution displays nothing ({len(src.splitlines())} lines)")
            if verbose:
                print("      " + src.strip()[:110])
    print(f"outputs: {bad} solutions that display nothing")
    return bad


CHECKS = {"runs": check_runs, "checks": check_checks, "outputs": check_outputs}


def main(argv: list[str]) -> int:
    verbose = "-v" in argv
    wanted = [a for a in argv if a in CHECKS] or list(CHECKS)
    return 1 if sum(CHECKS[name](verbose) for name in wanted) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
