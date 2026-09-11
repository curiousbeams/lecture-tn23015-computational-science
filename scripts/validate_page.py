"""Execute a converted page's marimo cells in order and triage the failures.

Student stubs are *meant* to fail (they are fill-in-the-blank, and marimo tolerates runtime
errors in authored cells). Solutions, the answer bank, and the checker are not: a failure there
is a porting bug. This script separates the two so the noise in the build output is actionable.

Usage:
    .venv/bin/python scripts/validate_page.py 01.numerical-differentiation.md
"""

from __future__ import annotations

import contextlib
import re
import signal
import sys
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parent.parent
CELL_RE = re.compile(r"^```\{marimo\}\s+python\s*$", re.M)


def extract_cells(path: Path) -> list[str]:
    return [src for src, _ in extract_cells_tagged(path)]


def extract_cells_tagged(path: Path) -> list[tuple[str, bool]]:
    """Return (source, in_solution) for each marimo cell, tracking the solution gates."""
    lines = path.read_text(encoding="utf-8").split("\n")
    cells, i, in_solution = [], 0, False
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith(":::{solution-start}"):
            in_solution = True
        elif stripped.startswith(":::{solution-end}"):
            in_solution = False
        elif stripped == "```{marimo} python":
            i += 1
            while i < len(lines) and lines[i].startswith(":"):  # directive options
                i += 1
            body = []
            while i < len(lines) and lines[i].strip() != "```":
                body.append(lines[i])
                i += 1
            cells.append(("\n".join(body).strip("\n"), in_solution))
        i += 1
    return cells


def page_header_source(path: Path) -> str:
    """The Python inside the page's `header: |` block scalar.

    The header is a setup cell: it executes in the browser but renders nothing, which is where
    the answer bank and the checker live. It never appears as a `{marimo}` cell, so it has to be
    pulled out of the config block by hand.
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    try:
        start = next(i for i, ln in enumerate(lines) if ln.rstrip() == "header: |")
    except StopIteration:
        return ""
    body = []
    for ln in lines[start + 1:]:
        if ln.strip() and not ln.startswith("  "):
            break
        body.append(ln[2:] if ln.startswith("  ") else "")
    return "\n".join(body)


def duplicate_globals(cells: list[str]) -> dict[str, list[int]]:
    """Globals bound by more than one cell -- marimo's one-definition-per-global rule.

    Underscore-prefixed names are cell-local in marimo and are exempt. Uses the same scoping rule
    as the converter: loops and conditionals do not create a scope, function and class bodies do.
    """
    import sys as _sys
    from collections import defaultdict
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
    from dag_collisions import bound_names

    owners: dict[str, list[int]] = defaultdict(list)
    for idx, src in enumerate(cells):
        for name in bound_names(src):
            if not name.startswith("_"):
                owners[name].append(idx)
    return {n: idxs for n, idxs in owners.items() if len(idxs) > 1}


def classify(src: str, in_solution: bool = False) -> str:
    if in_solution:
        return "solution"
    if src.startswith("ANSWERS ="):
        return "answers"
    if "def check_answers" in src:
        return "checker"
    if "def _solution" in src:
        return "solution"
    if "check_answers(" in src:
        return "check"
    if "mo.ui.run_button" in src:
        return "button"
    return "stub"


class FakeButton:
    value = True


class FakeValue:
    """Stands in for a marimo UI element; `.value` must be numeric for sliders."""

    def __init__(self, value):
        self.value = value


class FakeUI:
    def run_button(self, **kw):
        return FakeButton()

    def slider(self, *a, **kw):
        if "value" in kw:
            return FakeValue(kw["value"])
        return FakeValue(a[0] if a else 0)

    def dropdown(self, *a, **kw):
        return FakeValue(kw.get("value"))

    def checkbox(self, *a, **kw):
        return FakeValue(bool(kw.get("value", False)))


class StopSignal(BaseException):
    """A clean `mo.stop`, not a failure: marimo renders the message and skips descendants."""


class CellTimeout(BaseException):
    """A cell exceeded the per-cell budget -- reported, not treated as a failure."""


@contextlib.contextmanager
def time_limit(seconds: float):
    """Abort a cell that runs too long.

    Some reference solutions are genuinely slow -- PDE1 relaxes a 101x101 grid to 1e-4 in pure
    Python, several times over -- so a linear sweep of the whole book would otherwise look like
    a hang. SIGALRM only interrupts the main thread, which is where cells run.
    """

    def handler(signum, frame):
        raise CellTimeout

    previous = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


class FakeMo:
    ui = FakeUI()

    @staticmethod
    def md(text):
        return text

    @staticmethod
    def callout(body, kind="neutral"):
        return f"[{kind}] {body}"

    @staticmethod
    def accordion(items, **kw):
        return items

    @staticmethod
    def hstack(items, **kw):
        return items

    @staticmethod
    def vstack(items, **kw):
        return items

    @staticmethod
    def stop(pred, output=None):
        if pred:
            raise StopSignal(output)


def run(path: Path, budget: float = 20.0) -> int:
    import matplotlib.pyplot as plt
    import numpy as np

    tagged = extract_cells_tagged(path)
    cells = [c for c, _ in tagged]
    ns: dict = {"np": np, "plt": plt, "mo": FakeMo()}
    # The page's {marimo-config} header -- imports, the answer bank and the checker. It is a
    # YAML block scalar, so it is recovered by dedenting, not by a one-line regex.
    src = page_header_source(path)
    if src:
        # Plain exec cannot reproduce marimo's cell-local names, so this has to be checked
        # structurally: the header is one setup cell, and anything it defines with a leading
        # underscore is invisible to every other cell on the page.
        from dag_collisions import bound_names

        locals_ = sorted(n for n in bound_names(src) if n.startswith("_"))
        if locals_:
            print(f"HEADER DEFINES CELL-LOCAL NAMES (drop the underscore): {locals_}")
            return 1
        try:
            exec(src, ns)
        except Exception as e:  # noqa: BLE001
            print(f"HEADER FAILED: {type(e).__name__}: {e}")
            return 1
    # The header imports the real marimo; swap in the stub so run buttons read as "pressed"
    # and mo.stop does not abort the sweep.
    ns["mo"] = FakeMo()

    counts: dict[str, list[int]] = {}
    failures: list[tuple[int, str, str]] = []
    stopped: list[int] = []
    slow: list[int] = []

    for idx, (src, in_sol) in enumerate(tagged):
        kind = classify(src, in_sol)
        counts.setdefault(kind, [])
        try:
            with time_limit(budget):
                exec(src, ns)
        except CellTimeout:
            slow.append(idx)
        except StopSignal:
            stopped.append(idx)
        except BaseException:  # noqa: BLE001
            counts[kind].append(idx)
            tb = traceback.format_exc().strip().split("\n")[-1]
            failures.append((idx, kind, tb))
        finally:
            plt.close("all")

    total = len(cells)
    timed = f", {len(slow)} over {budget:g}s" if slow else ""
    print(f"{path.name}: {total} marimo cells ({len(stopped)} gated by mo.stop{timed})")
    for kind in ("answers", "checker", "button", "stub", "check", "solution"):
        n = sum(1 for c, s_ in tagged if classify(c, s_) == kind)
        bad = len(counts.get(kind, []))
        note = " (expected: unfilled stubs)" if kind in ("stub", "check") and bad else ""
        flag = "" if kind in ("stub", "check") or bad == 0 else "   <-- SHOULD BE ZERO"
        flag = flag + note
        print(f"  {kind:9s} {n:3d} cells, {bad:3d} failed{flag}")

    # marimo refuses to run a cell that redefines a global owned by another cell ("CELL NOT RUN
    # ... x_sol was also defined by cell-19"). That never raises during a linear sweep, so it
    # has to be checked structurally.
    dupes = duplicate_globals(cells)
    if dupes:
        print("\nGlobals defined by more than one cell (marimo will refuse to run these):")
        for name, idxs in sorted(dupes.items()):
            print(f"  {name:28s} cells {idxs}")

    def expected(idx, kind, tb):
        if kind == "stub":
            return True
        # the student has not filled the stub yet, so answer_* is undefined; marimo will not
        # run a descendant of a failed cell, so this never surfaces to the reader
        return kind == "check" and "NameError" in tb and "answer_" in tb

    unexpected = [f for f in failures if not expected(*f)]
    if unexpected:
        print("\nUnexpected failures:")
        for idx, kind, tb in unexpected:
            print(f"  cell {idx:3d} [{kind}] {tb}")
            print("      " + cells[idx].strip().split("\n")[0][:100])
    return 1 if unexpected else 0


if __name__ == "__main__":
    args = sys.argv[1:] or ["01.numerical-differentiation.md"]
    args = [a for a in args if not a.startswith("-")]
    rc = 0
    for a in args:
        rc |= run(ROOT / a)
    raise SystemExit(rc)
