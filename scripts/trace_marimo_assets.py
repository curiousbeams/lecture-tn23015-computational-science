"""Record which of marimo's assets a chapter actually fetches, by running it in a browser.

    .venv/bin/python scripts/trace_marimo_assets.py            # every chapter
    .venv/bin/python scripts/trace_marimo_assets.py 03.root-finding

Writes `scripts/marimo_assets_used.txt`, which `build_marimo_apps.sh` uses to drop the rest.

`marimo export html-wasm` ships marimo's whole editor: 728 files, 28 MB, of which `index.html`
loads only 192. The remaining 536 are lazily imported -- CodeMirror grammars for two dozen
languages, every Mermaid diagram type, a SQL parser, Vega, cytoscape -- and a Python notebook
touches almost none of them. Guessing which by filename would be exactly the kind of reasoning
that has already cost this project a day, so this measures it: load the page, let Pyodide boot and
every cell run, and record what the browser asked for.

**What this does and does not prove.** The browser boots the page, Pyodide downloads from
jsdelivr and micropip installs numpy/matplotlib/scipy -- all of that is captured, and the pruned
bundle serves every request with no 404s. But headless chromium never got as far as *executing*
the cells: seven minutes in, no output and no `<img>`, while the same bundle runs fine in a real
browser. So this is a **lower bound** -- chunks fetched only when a cell renders its output are
not in it. Open one chapter in a real browser and check a figure and a check cell before
deploying a pruned bundle:

    python -m http.server --directory marimo-apps   # then open /03.root-finding/

Needs playwright and its chromium:

    uv run --no-project --with playwright playwright install chromium
"""

from __future__ import annotations

import http.server
import socketserver
import sys
import threading
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "marimo-apps"
OUT = ROOT / "scripts" / "marimo_assets_used.txt"
SETTLE_MS = 20_000   # Pyodide boots, installs the wheel, then runs every cell


def serve(directory: Path):
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def trace(chapters: list[str]) -> set[str]:
    from playwright.sync_api import sync_playwright

    httpd, port = serve(APPS)
    used: set[str] = set()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for slug in chapters:
                page = browser.new_context().new_page()
                page.on("request", lambda r: used.add(r.url.split(f":{port}/")[-1])
                        if f":{port}/" in r.url else None)
                page.goto(f"http://127.0.0.1:{port}/{slug}/index.html")
                page.wait_for_timeout(SETTLE_MS)
                hits = len([u for u in used if u.startswith("assets/")])
                print(f"  {slug:44} {hits:>4} assets seen so far")
                page.close()
            browser.close()
    finally:
        httpd.shutdown()
    return {u.split("assets/", 1)[1] for u in used if u.startswith("assets/")}


def main(argv: list[str]) -> int:
    chapters = argv or sorted(d.name for d in APPS.iterdir()
                              if d.is_dir() and d.name[0].isdigit())
    if not chapters:
        raise SystemExit("no marimo-apps/<chapter>/ -- run scripts/build_marimo_apps.sh first")
    used = trace(chapters)
    # whatever index.html loads eagerly is required whether or not a request was recorded
    boot = set()
    for slug in chapters:
        text = (APPS / slug / "index.html").read_text(encoding="utf-8")
        boot |= {ln.split("../assets/")[1] for ln in text.split('"') if ln.startswith("../assets/")}
    keep = sorted(used | boot)
    OUT.write_text("\n".join(keep) + "\n", encoding="utf-8")
    have = len(list((APPS / "assets").iterdir()))
    print(f"\n{len(keep)} of {have} assets are used ({len(boot)} eager, {len(used)} fetched)")
    print(f"written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
