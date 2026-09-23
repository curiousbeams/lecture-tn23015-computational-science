"""Check that what was built actually reached Curvenote's CDN.

    .venv/bin/python scripts/check_deploy.py            # a stratified sample, fast
    .venv/bin/python scripts/check_deploy.py --all      # every static file, slow
    .venv/bin/python scripts/check_deploy.py --key <k>  # a specific deploy

Worth having because a submission can report success while a large part of it is missing. One
upload was interrupted partway through `marimo-apps/assets/`; the *next* submission then said
"49/1512 files need to be uploaded" and skipped the rest, because staging believed they were
already stored. The result was a deploy that served `index.html` and the first third of the
assets alphabetically, and 404ed the remainder -- a page that loads and then dies in the console.

So a green submit is not evidence. This asks the CDN.
"""

from __future__ import annotations

import json
import sys
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


def status(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:  # noqa: BLE001 - a transport failure is as bad as a 404 here
        return 0


def main(argv: list[str]) -> int:
    base = f"{CDN}/{cdn_key(argv)}/public"
    everything = sorted(p.relative_to(BUILD).as_posix()
                        for d in ("jupyter-lite", "marimo-apps") if (BUILD / d).is_dir()
                        for p in (BUILD / d).rglob("*") if p.is_file())
    if not everything:
        raise SystemExit(f"nothing to check under {BUILD}; run the site build first")

    # A stratified sample catches a truncated upload, which is contiguous in sort order; `--all`
    # is for when something is already known to be wrong and the extent matters.
    paths = everything if "--all" in argv else everything[:: max(1, len(everything) // 120)]
    print(f"{base}\n{len(paths)} of {len(everything)} static files")

    with ThreadPoolExecutor(max_workers=16) as pool:
        codes = list(pool.map(lambda p: status(f"{base}/{p}"), paths))

    missing = [p for p, c in zip(paths, codes) if c != 200]
    for path in missing[:15]:
        print(f"  {path}")
    if len(missing) > 15:
        print(f"  ... and {len(missing) - 15} more")
    print(f"\n{len(paths) - len(missing)} present, {len(missing)} missing")
    if missing:
        print("A submission can report success while missing files: staging deduplicates against\n"
              "what it believes is stored, so an interrupted upload is never retried. Re-submit\n"
              "and check again; if the same files are still missing, it needs Curvenote's side.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
