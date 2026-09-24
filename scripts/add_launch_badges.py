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

# Curvenote serves `static_files` from `pub.curvenote.com/<cdnKey>/public/`, and **the cdnKey is
# different for every submission** -- which is why a hardcoded one was wrong twice over: it was a
# stale key, and it would have gone stale again at the next deploy. It is not the work id either
# (that is stable, but nothing is served under it).
#
# The key of the last submission is in the build log, so that is where this reads it from:
#
#     _build/logs/curvenote.submit.json  ->  job.results.cdnKey
#
# Old keys keep serving (measured: a submission from the day before is still 200), so once the
# badges point at a deploy that contains the bundles they keep working. The order is therefore:
# submit, run this, submit again -- and after that only when the notebooks themselves change.
#
# Every link ends in an explicit file. `pub.curvenote.com` is object storage -- it has no
# directory indexes, so `.../lab/` is a 404 (`NoSuchKey`) while `.../lab/index.html` is a 200.
CDN = "https://pub.curvenote.com"
SUBMIT_LOG = ROOT / "_build" / "logs" / "curvenote.submit.json"


def cdn_key(argv: list[str]) -> str:
    """The cdnKey to point the badges at: `--key <uuid>`, else the last submission's."""
    if "--key" in argv:
        return argv[argv.index("--key") + 1]
    if not SUBMIT_LOG.exists():
        raise SystemExit(f"no {SUBMIT_LOG.relative_to(ROOT)}; submit once, or pass --key <uuid>")
    import json
    return json.loads(SUBMIT_LOG.read_text())["job"]["results"]["cdnKey"]

TITLE = ":::{admonition} Rather work in a notebook?"
LITE_BADGE = "https://jupyterlite.rtfd.io/en/stable/_static/badge-launch.svg"
MARIMO_BADGE = "https://marimo.io/shield.svg"
ANCHOR = ":::{exercise-start}"


def block(slug: str, base: str) -> str:
    return "\n".join([
        TITLE,
        ":class: seealso",
        "",
        "The same exercises, without the surrounding explanation, running in your browser.",
        "Nothing to install — and nothing is saved, so download your work before you close the tab.",
        "",
        f"[![launch lite]({LITE_BADGE})]({base}/jupyter-lite/lab/index.html?path={slug}.ipynb)",
        f"[![open in marimo]({MARIMO_BADGE})]({base}/marimo-apps/{slug}/index.html)",
        ":::",
    ])


def apply(path: Path, base: str) -> tuple[str, bool]:
    """(new text, changed). The block goes immediately before the chapter's first exercise.

    Not at the top of the chapter: these are an alternative way to do the *exercises*, so the
    reader meets them where there is first something to do. Every chapter now introduces its
    exercises under a heading that names the topic -- there is no generic "Exercises" section to
    anchor to, and there should not be -- so the first `{exercise-start}` is what means the same
    thing in all eleven.
    """
    text = path.read_text(encoding="utf-8")
    lines = strip_block(text.split("\n"))
    at = next(i for i, ln in enumerate(lines) if ln.startswith(ANCHOR))
    lines[at:at] = [*block(path.stem, base).split("\n"), ""]
    return "\n".join(lines), "\n".join(lines) != text


def strip_block(lines: list[str]) -> list[str]:
    """The page without its badge block, wherever it currently sits."""
    if TITLE not in lines:
        return lines
    start = lines.index(TITLE)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].rstrip() == ":::")
    del lines[start:end + 1]
    while start < len(lines) and not lines[start].strip():
        del lines[start]
    while start and not lines[start - 1].strip():
        del lines[start - 1]
        start -= 1
    lines[start:start] = [""]
    return lines


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    base = f"{CDN}/{cdn_key(argv)}/public"
    changed = []
    for path in sorted(ROOT.glob("[01][0-9].*.md")):
        if path.name.startswith("00."):
            continue
        new, differs = apply(path, base)
        if not differs:
            continue
        changed.append(path.name)
        if not check_only:
            path.write_text(new, encoding="utf-8")
    verb = "missing or stale" if check_only else "updated"
    print(f"cdnKey: {base}")
    print(f"{len(changed)} chapter badge block(s) {verb}"
          + (f": {', '.join(changed)}" if changed else ""))
    return 1 if check_only and changed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
