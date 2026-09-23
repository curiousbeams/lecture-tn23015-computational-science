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
    grading   every check cell grades the stored answers green. The answers are matched to the
              call *by position* -- the first argument is compared against `..._1` -- while the
              reader sees them by name, so a reordered call would silently grade correct work
              wrong. Feeding the reference values back in is the only thing that catches it

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
    """No solution renders an empty cell.

    Solutions are executable *because* their output is the teaching. They used to live in the
    chapters and were swept from there; `strip_solutions.py` took them off the website, so this
    reads the ground-truth notebooks instead -- same cells, same rule, and the coverage does not
    quietly go to zero just because the markdown no longer has them.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from sync_cells import notebook_cells

    notebooks = sorted((V.ROOT / "marimo-notebooks").glob("[01][0-9].*.py"))
    if not notebooks:
        print("outputs: no marimo-notebooks/ -- nothing to check")
        return 0
    bad = seen = 0
    for nb in notebooks:
        for name, src in notebook_cells(nb).items():
            if not name.startswith("sol_"):
                continue
            seen += 1
            if re.search(r"^show\([^)]", src, re.M) or "print(" in src:
                continue
            bad += 1
            print(f"  {nb.name} {name}: displays nothing ({len(src.splitlines())} lines)")
            if verbose:
                print("      " + src.strip()[:110])
    print(f"outputs: {bad} of {seen} solutions display nothing")
    return bad


def check_grading(verbose: bool) -> int:
    """Replay each check cell with the stored answers, then with one of them spoiled."""
    bad = 0
    for name in CHAPTERS:
        path = V.ROOT / name
        ns = page_namespace(path)
        if "ANSWERS" not in ns:
            continue  # the index and the about page carry no exercises
        answers, check = ns["ANSWERS"], ns["check_answers"]
        for src, _ in V.extract_cells_tagged(path):
            call = check_call(src)
            if call is None:
                continue
            labels, key, start = call
            keys = [f"{key}_{i}" for i in range(start, start + len(labels))]
            missing = [k for k in keys if k not in answers]
            if missing:
                # Pre-existing gaps in the source answer bank; the checker skips them and says so.
                print(f"  note: {name} {key} has no stored answer for {missing}")
            if any(isinstance(answers.get(k), dict) and answers[k].get("__downsampled__")
                   for k in keys):
                continue  # a downsampled answer is not its own input; nothing to replay
            # a key with no stored answer is skipped by the checker, so anything stands in for it
            values = [ns["to_array"](answers[k]) if k in answers else 0.0 for k in keys]
            got = str(check(**dict(zip(labels, values)), key=key, start=start))
            if "[success]" not in got:
                bad += 1
                print(f"  {name} {key}: correct answers did not grade green -- {got[:160]}")
                continue
            # and a wrong one has to be reported against the name the reader typed
            if keys[0] in answers:
                spoiled = [values[0] * 2 + 1, *values[1:]]
                got = str(check(**dict(zip(labels, spoiled)), key=key, start=start))
                if "[danger]" not in got or f"`{labels[0]}`" not in got:
                    bad += 1
                    print(f"  {name} {key}: a wrong `{labels[0]}` went unreported -- {got[:160]}")
            if verbose:
                print(f"  {name} {key}: {', '.join(labels)}")
    print(f"grading: {bad} check cells that do not grade their own answer key")
    return bad


def check_call(src: str):
    """(labels, key, start) for a `check_answers(...)` cell, or None if this is not one."""
    import ast

    src = src.strip()
    if not src.startswith("check_answers("):
        return None
    call = ast.parse(src).body[0].value
    labels = [kw.arg for kw in call.keywords if kw.arg not in ("key", "start", "when")]
    const = {kw.arg: kw.value.value for kw in call.keywords
             if kw.arg in ("key", "start") and isinstance(kw.value, ast.Constant)}
    return labels, const["key"], const.get("start", 1)


PLOT_WORD = re.compile(r"(?i)\b(plot|graph|histogram|scatter|imshow|figure)\b")
SUBPLOTS = re.compile(r"^_fig\s*,\s*_ax\w*\s*=\s*plt\.subplots")
# Anchored hard at column zero. An earlier `^[\w ,=]*` let the space class swallow indentation,
# so a draw call inside `if given(...):` counted as one that happens on load -- and the check
# passed over every cell that creates its axes eagerly and only fills it once the reader starts.
DRAWS = re.compile(r"^(?:\w+(?:\s*,\s*\w+)*\s*=\s*)?_ax\w*\."
                   r"(plot|imshow|hist|scatter|bar|semilog|loglog|errorbar"
                   r"|step|contour|pcolor|fill|axhline|axvline)")
MARKERS = ("# Do not edit or remove the boiler-plate code below.",
           "# Fill in the commented lines below, but leave the rest of this block in place.")


def editable_cells(path: Path):
    """(index, source) for the cells the reader can actually type into.

    `:editor: false` cells are read-only demonstrations -- the reader cannot delete their `show()`
    and has no blanks to fill, so none of the rules below apply to them. `extract_cells_tagged`
    drops the directive options, which is the difference that matters here.
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    i, idx, in_solution = 0, 0, False
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith(":::{solution-start}"):
            in_solution = True
        elif stripped.startswith(":::{solution-end}"):
            in_solution = False
        elif stripped == "```{marimo} python":
            i += 1
            opts = []
            while i < len(lines) and lines[i].startswith(":"):
                opts.append(lines[i].strip())
                i += 1
            body = []
            while i < len(lines) and lines[i].strip() != "```":
                body.append(lines[i])
                i += 1
            if ":editor: true" in opts and not in_solution:
                yield idx, "\n".join(body).strip("\n")
            idx += 1
        i += 1


def check_stubs(verbose: bool) -> int:
    """Three things a reader depends on that nothing else looks at.

    An exercise that says "now make a plot" has to hand `show()` something to draw on, or the
    reader writes `_ax.plot(...)`, runs the cell and sees nothing -- with no error to explain it.
    The axes is a blank like any other, so it starts as `None` and `show(_ax, ...)` ignores it
    until they uncomment `plt.subplots()`. Creating it eagerly instead would leave an empty pair
    of axes sitting in the cell on load, which is the other half of this check.

    And `show(...)` must never lose its warning: a cell whose output is None has no run button,
    so deleting that line costs the reader everything they have typed on the page.
    """
    bad = 0
    for name in CHAPTERS:
        for idx, src in editable_cells(V.ROOT / name):
            lines = src.split("\n")
            if not any(ln.startswith("show(") for ln in lines):
                continue
            shows_axes = bool(re.search(r"^show\(\s*\n?\s*_", src, re.M))
            has_axes = any(re.match(r"^\s*(_fig\s*,\s*)?_(ax|fig)\w*\s*=", ln) for ln in lines)
            prompts = [ln for ln in lines if ln.strip().startswith("#") and PLOT_WORD.search(ln)]

            if prompts and not (has_axes and shows_axes):
                bad += 1
                print(f"  {name} cell {idx}: asks for a plot with no axes to draw on")
            if any(SUBPLOTS.match(ln) for ln in lines) and not any(DRAWS.match(ln) for ln in lines):
                bad += 1
                print(f"  {name} cell {idx}: renders an empty axes on load")
            if not any(m in lines for m in MARKERS):
                bad += 1
                print(f"  {name} cell {idx}: show() carries no do-not-edit warning")
            if verbose and prompts:
                print(f"  {name} cell {idx}: {prompts[0].strip()[:80]}")
    print(f"stubs:   {bad} exercise cells that would mislead the reader")
    return bad


CHECKS = {"runs": check_runs, "checks": check_checks, "outputs": check_outputs,
          "grading": check_grading, "stubs": check_stubs}


def main(argv: list[str]) -> int:
    verbose = "-v" in argv
    wanted = [a for a in argv if a in CHECKS] or list(CHECKS)
    return 1 if sum(CHECKS[name](verbose) for name in wanted) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
