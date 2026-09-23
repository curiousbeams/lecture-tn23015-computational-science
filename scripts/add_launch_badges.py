"""Put the "launch lite" and "open in marimo" badges on every chapter.

    .venv/bin/python scripts/add_launch_badges.py
    .venv/bin/python scripts/add_launch_badges.py --check

Idempotent: the block is found by its title and replaced, so re-running after changing `BASE`
rewrites all eleven rather than adding a second copy. That is the point of having it in a script
-- the deploy URL is one edit here, not eleven edits across the chapters.

Both badges are the projects' own: `jupyterlite.rtfd.io/.../badge-launch.svg` reads "launch lite",
and `marimo.io/shield.svg` reads "open in marimo". marimo also publishes `molab-shield.svg`, which
reads "Open in molab" -- that is their hosted service, and these notebooks are a self-hosted WASM
export, so it would be a lie.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Where the two bundles are served from. `scripts/build_jupyter_lite.sh` and `scripts/build_marimo_apps.sh`
# produce `jupyter-lite/` and `marimo-apps/`; both are gitignored and have to be built before a deploy.
BASE = "https://pub.curvenote.com/01a0c9a4-6035-7805-b31e-890427f99eee/public"

TITLE = ":::{admonition} Rather work in a notebook?"
LITE_BADGE = "https://jupyterlite.rtfd.io/en/stable/_static/badge-launch.svg"
MARIMO_BADGE = "https://marimo.io/shield.svg"
ANCHOR = ":::{admonition} Learning goals"


def block(slug: str) -> str:
    return "\n".join([
        TITLE,
        ":class: seealso",
        "",
        "The same exercises, without the surrounding explanation, running in your browser.",
        "Nothing to install — and nothing is saved, so download your work before you close the tab.",
        "",
        f"[![launch lite]({LITE_BADGE})]({BASE}/jupyter-lite/lab/index.html?path={slug}.ipynb)",
        f"[![open in marimo]({MARIMO_BADGE})]({BASE}/marimo-apps/{slug}/)",
        ":::",
    ])


def apply(path: Path) -> tuple[str, bool]:
    """(new text, changed). Replaces an existing block, or inserts one after the learning goals."""
    text = path.read_text(encoding="utf-8")
    want = block(path.stem)
    if TITLE in text:
        start = text.index(TITLE)
        end = text.index("\n:::", text.index("\n", start)) + len("\n:::")
        new = text[:start] + want + text[end:]
    else:
        lines = text.split("\n")
        at = next(i for i, ln in enumerate(lines) if ln.startswith(ANCHOR))
        close = next(i for i in range(at + 1, len(lines)) if lines[i].rstrip() == ":::")
        lines[close + 1:close + 1] = ["", *want.split("\n")]
        new = "\n".join(lines)
    return new, new != text


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    changed = []
    for path in sorted(ROOT.glob("[01][0-9].*.md")):
        if path.name.startswith("00."):
            continue
        new, differs = apply(path)
        if not differs:
            continue
        changed.append(path.name)
        if not check_only:
            path.write_text(new, encoding="utf-8")
    verb = "missing or stale" if check_only else "updated"
    print(f"{len(changed)} chapter badge block(s) {verb}"
          + (f": {', '.join(changed)}" if changed else ""))
    return 1 if check_only and changed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
