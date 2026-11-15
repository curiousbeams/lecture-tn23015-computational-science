"""Let a student pick up their marimo work again: from the page address, or from a saved file.

    .venv/bin/python scripts/make_marimo_continue.py marimo-apps

Run by `build_marimo_apps.sh` after the chapters are exported. It patches every chapter's
`index.html` and writes, beside the apps:

    continue.js                 the "continue a saved notebook" widget (an anywidget module)
    continue.html               a page that shows the same widget, for links from inside the apps
    public/lz-string.min.js     the codec marimo uses for `#code/`, for the patch (a classic script)

**What marimo does on its own.** In the WASM build, Ctrl+S writes the whole notebook into the page
address as `#code/<lz-string>`, and Download → Download notebook source saves the same text as a
file. On load, marimo takes its code from the first of: the `<marimo-code>` element baked into the
page, then the address. The baked copy is always there, so saved work was never read back.

The saved text also differs from the baked copy in two ways, and both matter:

- it has lost the `# /// script` header. That header names the `tn23015` wheel, and it is the
  only thing that makes the browser install the module, so saved code fails at its first import.
- `marimo.App(width="medium")` has become `marimo.App()`.

**The patch.** A short script runs while each chapter page is parsed, before marimo's own module
starts. If the address carries `#code/…`, it decompresses that code, gives it this page's header
and `App(...)` line, and writes the result into `<marimo-code>`, where marimo looks first. The
header always comes from the page doing the loading, so the wheel is always the one this deploy
ships. Its name carries a content hash, so a header from an older deploy would name a wheel that is
gone. A notebook from the marimo zip, which never had a header, gets one the same way.

So reloading a saved page, reopening a closed tab, or a bookmark brings the work back. The badge
link has no `#code/` part, so it always opens the current notebook, and a saved copy never hides a
corrected one. That trade-off is also why JupyterLite keeps its default per-URL storage.

**The widget** is the way back from a file. The student picks a `.py` (a download from the browser
version, or a notebook from the marimo zip). It is read in the browser and nothing is uploaded: the
widget only compresses it into the chapter's address, and the patch does the rest. It lives in two
places, with one implementation:

- in the book, inside each chapter's "Rather work in a notebook?" block, as a MyST `{anywidget}`
  (`add_launch_badges.py` writes it, with the chapter's slug and the apps' address). It opens the
  app in a new tab.
- `continue.html`, which the note at the top of each browser notebook links to (as
  `continue.html?chapter=<slug>`). It mounts the same module and opens the app in the same tab.

The chapter is recognised from the file, because every chapter's answer keys share a number of
their own (`answer_5_…` is Root Finding). A file from another chapter opens in its own chapter.

**The module must not depend on its own address.** MyST copies every `{anywidget}` module into the
site's `public/` under a hashed name, whether it is given as a path or a URL (a URL is downloaded
at build time). So in the book, `import.meta.url` is that copy, not the apps folder. That is why
lz-string is pasted into the module rather than imported, and why the book passes the apps' address
as `apps`; only `continue.html`, which loads the file where it lies, falls back to the module's own
address. The book points the widget at the local `marimo-apps/continue.js`, so every build has the
current one. An earlier version pointed it at the previous deploy's copy on the CDN: on the first
deploy after the widget was added, that copy did not exist, and the build saved the CDN's 404 page
as the module ("Unexpected token '<'").

lz-string is vendored (`scripts/vendor/`), not loaded from a CDN: the patch needs it synchronously,
before marimo starts, and a same-origin file is one cached request with nothing else to fail. The
widget carries its own copy, as above.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_notebooks import ROOT  # noqa: E402

LZ_STRING = Path(__file__).resolve().parent / "vendor" / "lz-string.min.js"

# Runs while the page is parsed, so before marimo's deferred module script reads `<marimo-code>`.
# Every step falls back to the baked notebook: no LZString, a hash that does not decompress.
RESTORE = r"""<script src="../public/lz-string.min.js"></script>
<script data-tn23015="restore">
  // TN23015 (scripts/make_marimo_continue.py): marimo's Ctrl+S saves the notebook into this page's
  // address (#code/...), but on load it reads the copy baked into the page first, and the saved copy
  // has lost the header that installs the tn23015 module. So when the address carries saved code,
  // give it this page's header and put it where marimo looks first.
  (function () {
    if (location.hash.indexOf("#code/") !== 0 || typeof LZString === "undefined") return;
    var el = document.querySelector("marimo-code");
    var saved = LZString.decompressFromEncodedURIComponent(location.hash.slice(6));
    if (!el || !saved) return;
    var baked = decodeURIComponent(el.textContent);
    var header = (baked.match(/^# \/\/\/ script\n(?:#.*\n)*?# \/\/\/\n/) || [""])[0];
    var spec = /tn23015 @ [^"']*?\.whl/;
    var code = spec.test(saved) && spec.test(header)
      ? saved.replace(spec, header.match(spec)[0])
      : header + "\n" + saved;
    var app = baked.match(/^app = marimo\.App\(.*\)$/m);
    if (app) code = code.replace(/^app = marimo\.App\(\)$/m, app[0]);
    el.textContent = encodeURIComponent(code);
  })();
</script>"""

MODULE = r"""// TN23015: continue a saved marimo notebook in the browser version of its chapter.
//
// An anywidget. The book shows it in each chapter's "Rather work in a notebook?" block with
// {chapter: "<slug>", apps: "<address of marimo-apps/>"}; continue.html, beside this file, mounts it
// with the chapter from ?chapter= and {target: "_self"}. The file is read here and never uploaded:
// its code is compressed into the chapter's address as #code/..., which the chapter page loads.
//
// Self-contained on purpose: the book serves a copy of this file from elsewhere, so nothing may be
// resolved against its own address unless `apps` is missing (see make_marimo_continue.py).
//
// GENERATED by scripts/make_marimo_continue.py. Edit it there.

__LZSTRING__

const CHAPTERS = __CHAPTERS__;

const CSS = `
.tn-continue { display: grid; gap: 0.5rem; margin: 0.75rem 0 0.25rem; font: inherit; color: inherit; }
.tn-continue .tn-title { font-weight: 600; }
.tn-continue .tn-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; }
.tn-continue button, .tn-continue .tn-pick, .tn-continue select {
  font: inherit; font-size: 0.92em; color: inherit; background: transparent; cursor: pointer;
  border: 1px solid color-mix(in srgb, currentColor 35%, transparent); border-radius: 6px;
  padding: 0.3rem 0.75rem; line-height: 1.4;
}
.tn-continue button.tn-open:not(:disabled) { border-color: currentColor; font-weight: 600; }
.tn-continue button:disabled { opacity: 0.45; cursor: default; }
.tn-continue input[type=file] { display: none; }
.tn-continue .tn-name { font-size: 0.92em; opacity: 0.8; overflow-wrap: anywhere; }
.tn-continue .tn-status { font-size: 0.88em; opacity: 0.75; margin: 0; min-height: 1.3em; }
`;

function detect(text) {
  const key = text.match(/answer_(\d+)_/);
  const hit = key && CHAPTERS.find((c) => c.prefix === key[1]);
  return hit ? hit.slug : "";
}

function title(slug) {
  const hit = CHAPTERS.find((c) => c.slug === slug);
  return hit ? hit.title : slug;
}

export default {
  render({ model, el }) {
    const fixed = model.get("chapter") || "";
    const target = model.get("target") || "_blank";
    const root = document.createElement("div");
    root.className = "tn-continue";
    root.innerHTML = `<style>${CSS}</style>
      <div class="tn-title">Continue a saved marimo notebook</div>
      <div class="tn-row">
        <label class="tn-pick">Choose your .py file…<input type="file" accept=".py,text/x-python,text/plain"></label>
        <span class="tn-name"></span>
      </div>
      <div class="tn-row">
        <select aria-label="Chapter"${fixed ? " hidden" : ""}>
          <option value="">Chapter…</option>
          ${CHAPTERS.map((c) => `<option value="${c.slug}">${c.title}</option>`).join("")}
        </select>
        <button class="tn-open" disabled>Open in marimo</button>
      </div>
      <p class="tn-status" role="status"></p>`;
    el.appendChild(root);

    const input = root.querySelector("input");
    const name = root.querySelector(".tn-name");
    const select = root.querySelector("select");
    const open = root.querySelector("button");
    const status = root.querySelector(".tn-status");
    let code = null;
    select.value = fixed;

    const update = () => { open.disabled = !(code && select.value); };

    input.addEventListener("change", async () => {
      const file = input.files[0];
      code = null;
      name.textContent = file ? file.name : "";
      if (!file) { status.textContent = ""; update(); return; }
      const text = await file.text();
      if (!/import marimo/.test(text) || !/@app\.cell/.test(text)) {
        status.textContent = "This is not a marimo notebook. Choose the .py file you downloaded or saved.";
        update();
        return;
      }
      code = text;
      const found = detect(text);
      if (found) select.value = found;
      if (found && fixed && found !== fixed) {
        status.textContent = `This is your ${title(found)} notebook, so it opens in that chapter.`;
      } else if (found) {
        status.textContent = fixed ? "" : `This is your ${title(found)} notebook.`;
      } else {
        select.hidden = false;
        status.textContent = "Could not tell which chapter this is; choose it.";
      }
      update();
    });

    select.addEventListener("change", update);

    open.addEventListener("click", () => {
      if (!code || !select.value) return;
      const url = new URL(`${select.value}/index.html`, model.get("apps") || import.meta.url);
      url.hash = "code/" + LZString.compressToEncodedURIComponent(code);
      window.open(url.href, target);
    });
  },
};
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Continue a saved notebook · TN23015</title>
<style>
  :root { color-scheme: light dark; --fg: #1b1e23; --bg: #fff; --muted: #5b6270; }
  @media (prefers-color-scheme: dark) { :root { --fg: #e8eaee; --bg: #17191d; --muted: #a0a7b4; } }
  body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
  main { max-width: 40rem; margin: 0 auto; padding: 3rem 1.25rem; }
  h1 { font-size: 1.5rem; line-height: 1.25; margin: 0 0 1rem; }
  p { margin: 0 0 1rem; }
  .muted { color: var(--muted); font-size: 0.92rem; }
  #widget { margin: 1.5rem 0; }
</style>
</head>
<body>
<main>
  <h1>Continue a saved marimo notebook</h1>
  <p>Pick a notebook you saved from the book: one you downloaded from a chapter's marimo version
  (Download → Download notebook source), or one from the marimo notebooks download. It opens in
  the browser version of its chapter with your code in it.</p>
  <div id="widget"></div>
  <p class="muted">The file stays on your computer: it is read here and put into the page's
  address. Keep saving (Ctrl+S, or ⌘S on a Mac) as you work. Each save updates the address, so
  reloading the page, reopening the tab or a bookmark brings your work back.</p>
</main>
<script type="module">
  import widget from "./continue.js";
  const state = { chapter: new URLSearchParams(location.search).get("chapter") || "", target: "_self" };
  widget.render({ model: { get: (key) => state[key], on() {}, off() {} },
                  el: document.getElementById("widget") });
</script>
</body>
</html>
"""


def patch(index: Path) -> bool:
    """Put RESTORE straight after the page's <marimo-code>, replacing an older version. Idempotent."""
    before = index.read_text(encoding="utf-8")
    html = re.sub(r'\n(?:<script src="\.\./public/lz-string\.min\.js"></script>\n)?'
                  r'<script data-tn23015="restore">.*?</script>', "", before, flags=re.S)
    assert html.count("</marimo-code>") == 1, f"{index}: expected one <marimo-code> element"
    html = html.replace("</marimo-code>", "</marimo-code>\n" + RESTORE, 1)
    index.write_text(html, encoding="utf-8")
    return html != before


def chapters() -> list[dict[str, str]]:
    """slug, title, and the number every one of the chapter's answer keys starts with."""
    out = []
    for page in sorted(ROOT.glob("[01][0-9].*.md")):
        if page.name.startswith("00"):
            continue
        text = page.read_text(encoding="utf-8")
        title = re.search(r"^title:\s*(.+?)\s*$", text, re.M).group(1)
        prefixes = set(re.findall(r":label: ex_(\d+)_", text))
        assert len(prefixes) == 1, f"{page.name}: exercise keys with several prefixes {prefixes}"
        out.append({"slug": page.stem, "title": title, "prefix": prefixes.pop()})
    assert len({c["prefix"] for c in out}) == len(out), "two chapters share a key prefix"
    return out


def main(argv: list[str]) -> int:
    out = Path(argv[0]) if argv else ROOT / "marimo-apps"
    (out / "public").mkdir(parents=True, exist_ok=True)
    lz = LZ_STRING.read_text(encoding="utf-8")
    (out / "public" / "lz-string.min.js").write_text(lz, encoding="utf-8")
    (out / "public" / "lz-string.esm.js").unlink(missing_ok=True)      # no longer used
    patched = sum(patch(p) for p in sorted(out.glob("[01][0-9].*/index.html")))
    print(f"  {patched} chapter page(s) patched to restore saved work from the address")
    found = chapters()
    module = MODULE.replace("__CHAPTERS__", json.dumps(found)).replace("__LZSTRING__", lz.strip())
    (out / "continue.js").write_text(module, encoding="utf-8")
    (out / "continue.html").write_text(PAGE, encoding="utf-8")
    print(f"  {out.name}/continue.js + continue.html   {len(found)} chapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
