"""Check that what was built actually reached Curvenote's CDN.

    .venv/bin/python scripts/check_deploy.py            # every top-level file + a sample of the bundles
    .venv/bin/python scripts/check_deploy.py --all      # every file, slow
    .venv/bin/python scripts/check_deploy.py --key <k>  # a specific deploy

Worth having because a submission can report success while a large part of it is missing. For
weeks every deploy lost the alphabetical tail of its files -- first inside `marimo-apps/assets/`,
later the figures and page downloads that sort after `sampling4.png` -- and the submit said nothing.
Curvenote traced it (2026-10) to their publishing step: it copied staged files to the public CDN
from a `GoogleStorage.listObjects` call that returns 1000 objects per page, and never asked for the
second page. The files were in staging all along; they were just never published.

That is fixed on their side, but a green submit is still not evidence. This asks the CDN. Top-level
files (the figures, page downloads and widget modules) are few and are what readers see first, so
they are always checked in full; the two static bundles are sampled unless `--all` is given.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "_build" / "site" / "public"
SUBMIT_LOG = ROOT / "_build" / "logs" / "curvenote.submit.json"
CDN = "https://pub.curvenote.com"


def cdn_key(argv: list[str]) -> str:
    if "--key" in argv:
        return argv[argv.index("--key") + 1]
    if not SUBMIT_LOG.exists():
        raise SystemExit("no submit log; pass --key <uuid>")
    return json.loads(SUBMIT_LOG.read_text())["job"]["results"]["cdnKey"]


def status(url: str, attempts: int = 4) -> int:
    """HTTP status of a HEAD request. Transport failures are retried with a short backoff: a
    flaky connection once made a complete deploy look 30% missing. A 404 is final."""
    request = urllib.request.Request(url, method="HEAD")
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status
        except urllib.error.HTTPError as exc:
            if exc.code < 500:
                return exc.code
        except Exception:  # noqa: BLE001 - retried below, then reported as 0
            pass
        time.sleep(1 + 2 * attempt)
    return 0


def main(argv: list[str]) -> int:
    base = f"{CDN}/{cdn_key(argv)}/public"
    top = sorted(p.name for p in BUILD.iterdir() if p.is_file()) if BUILD.is_dir() else []
    bundles = sorted(p.relative_to(BUILD).as_posix()
                     for d in ("jupyter-lite", "marimo-apps") if (BUILD / d).is_dir()
                     for p in (BUILD / d).rglob("*") if p.is_file())
    if not top and not bundles:
        raise SystemExit(f"nothing to check under {BUILD}; run the site build first")

    # A stratified sample catches a truncated upload, which is contiguous in sort order; `--all`
    # is for when something is already known to be wrong and the extent matters.
    sample = bundles if "--all" in argv else bundles[:: max(1, len(bundles) // 120)]
    paths = top + sample
    print(f"{base}\n{len(top)} top-level files (all) + {len(sample)} of {len(bundles)} bundle files")

    with ThreadPoolExecutor(max_workers=16) as pool:
        codes = list(pool.map(lambda p: status(f"{base}/{p}"), paths))

    missing = [p for p, c in zip(paths, codes) if c != 200]
    for path in missing[:15]:
        print(f"  {path}")
    if len(missing) > 15:
        print(f"  ... and {len(missing) - 15} more")
    print(f"\n{len(paths) - len(missing)} present, {len(missing)} missing")
    if missing:
        print("A submission can report success while missing files. If they are a contiguous run\n"
              "at the end of the sort order, suspect the publishing step again (see the docstring)\n"
              "and tell Curvenote; a scattered few are more likely a network problem, so re-run.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
