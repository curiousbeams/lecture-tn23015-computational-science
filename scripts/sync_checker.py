"""Copy `checker.py` into every chapter's `{marimo-config}` header.

The header becomes a marimo *setup cell* that runs in the reader's browser, where there is no
filesystem and nothing to import, so the runtime has to be present in each page. MyST
substitutions do not reach directive options and the plugin has no include mechanism, which
leaves copying -- and copying is fine as long as one file is the source of truth and something
checks that the copies have not drifted.

That is this script. It refuses to write if the eleven existing copies disagree with each other,
because that means someone edited a page directly and their change is about to be lost.

    .venv/bin/python scripts/sync_checker.py           # write
    .venv/bin/python scripts/sync_checker.py --check   # verify only, non-zero if stale

Each chapter's header is: its own imports, its own `ANSWERS` bank, then this shared runtime. Only
the part after the answer bank is touched.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = sorted(
    p for p in ROOT.glob("[01][0-9].*.md") if not p.name.startswith(("00.", "00b."))
)
HEADER_OPEN = "header: |"
MODULE = ROOT / "packages" / "tn23015.py"
# marimo builds a wheel from every local module a notebook imports, and puts it in the WASM
# export's `public/wheels/`. It does not follow a symlink, so this copy has to be a real file.
MODULE_MARIMO = ROOT / "marimo-notebooks" / "tn23015.py"

# What the module needs and the page header does not: numpy (the header imports it above the
# copied body) and the answer bank (the converter writes it into the header as a literal).
MODULE_HEAD = '''"""The TN23015 runtime, for notebooks: everything an exercise calls that is not numpy.

GENERATED -- do not edit. `scripts/checker.py` is the source, and `scripts/sync_checker.py`
writes this file and the eleven chapter headers from it. Editing here is lost on the next sync,
and `sync_checker.py --check` fails until it is.

Drop this file next to the notebooks and `import tn23015`; `answers/*.json` are found beside it,
or anywhere above it, which covers both the JupyterLite bundle and a checkout of the repository.
"""

import numpy as np
'''

MODULE_TAIL = '''

CHAPTERS_JSON = [
    "fourier-transforms-1", "fourier-transforms-2", "linear-algebra",
    "numerical-differentiation", "numerical-integration",
    "ordinary-differential-equations-1", "ordinary-differential-equations-2",
    "partial-differential-equations-1", "partial-differential-equations-2",
    "random-numbers", "root-finding",
]


def _load_answers():
    """The answer bank, from `answers/*.json`.

    A notebook gets all eleven chapters at once, which is safe: the 128 keys do not collide. The
    marimo *pages* never call this -- their header carries their own chapter's bank as a literal,
    because an island has no filesystem to read from.

    Under a WASM export there is no filesystem either, but `public/answers/` is served beside the
    notebook, so the files are fetched. That is why the chapter list is hard-coded: a URL cannot
    be globbed.
    """
    import json
    from pathlib import Path

    local = local_asset("answers", CHAPTERS_JSON[0] + ".json")
    if local is not None:
        return {k: v for path in sorted(local.parent.glob("*.json"))
                for k, v in json.loads(path.read_text()).items()}
    bank = {}
    for name in CHAPTERS_JSON:
        for url in asset_urls("answers", name + ".json"):
            try:
                bank.update(json.loads(fetch(url).read()))
                break
            except Exception:             # noqa: BLE001 - a missing chapter is not fatal
                continue
    return bank


ANSWERS = _load_answers()
'''


def module_source(runtime: str) -> str:
    """`packages/tn23015.py`: the shared runtime with the module-only prologue and epilogue."""
    return MODULE_HEAD + "\n" + runtime.strip("\n") + "\n" + MODULE_TAIL


def runtime_source() -> str:
    """checker.py without its module docstring, which is for maintainers, not the browser."""
    text = (ROOT / "scripts" / "checker.py").read_text()
    end = text.index('"""', text.index('"""') + 3) + 3
    return text[end:].strip("\n")


def split_header(path: Path) -> tuple[list[str], int, int, int]:
    """(lines, first line of the header body, line after it, line where the runtime starts)."""
    lines = path.read_text().split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.rstrip() == HEADER_OPEN) + 1
    end = start
    while end < len(lines) and (not lines[end].strip() or lines[end].startswith("  ")):
        end += 1
    # the answer bank ends at its closing brace; the runtime is everything after it
    close = max(i for i in range(start, end) if lines[i].rstrip() == "  }")
    return lines, start, end, close + 1


def current_runtime(path: Path) -> str:
    lines, _, end, begin = split_header(path)
    body = [ln[2:] if ln.startswith("  ") else ln for ln in lines[begin:end]]
    return "\n".join(body).strip("\n")


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    want = runtime_source()

    have = {}
    for p in CHAPTERS:
        have.setdefault(hashlib.sha256(current_runtime(p).encode()).hexdigest(), []).append(p.name)
    if len(have) > 1 and not check_only:
        print("Refusing to write: the chapters' copies have drifted apart.")
        for digest, names in have.items():
            print(f"  {digest[:12]}  {', '.join(names)}")
        print("Reconcile them by hand, or copy the one you want into scripts/checker.py first.")
        return 1

    stale = [p for p in CHAPTERS if current_runtime(p) != want]
    module = module_source(want)
    for dest in (MODULE, MODULE_MARIMO):
        if not dest.exists() or dest.read_text() != module:
            stale.append(dest)
    if check_only:
        for p in stale:
            print(f"  stale: {p.name}")
        print(f"{len(stale)} of {len(CHAPTERS) + 2} copies differ from scripts/checker.py")
        return 1 if stale else 0

    indented = ["  " + ln if ln.strip() else "" for ln in want.split("\n")]
    for p in stale:
        if p in (MODULE, MODULE_MARIMO):
            p.write_text(module)
        else:
            lines, _, end, begin = split_header(p)
            p.write_text("\n".join([*lines[:begin], *indented, *lines[end:]]))
        print(f"  updated {p.relative_to(ROOT)}")
    print(f"{len(stale)} copy(s) synced from scripts/checker.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
