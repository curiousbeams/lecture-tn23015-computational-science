#!/usr/bin/env bash
# Build the "Open in marimo" apps: one editable WASM notebook per chapter, statically served.
#
# `marimo export html-wasm --mode edit` produces a self-contained Pyodide app per notebook. There
# is no supported way to share anything between exports -- the docs say plainly that multiple
# notebooks need separate runs -- and eleven untouched exports come to ~310 MB, almost all of it
# eleven identical copies of marimo's own JavaScript. So this shares them afterwards.
#
# **Everything shared has to move together.** `mo.notebook_location()` is derived by taking the
# URL of marimo's own web worker and crawling *out of* `assets/`:
#
#     .../03.root-finding/assets/worker-X.js  ->  .../03.root-finding
#     .../assets/worker-X.js                  ->  ...              (the server root)
#
# So the moment `assets/` is shared at the top, every path the notebook resolves at runtime moves
# to the top with it -- the answer bank, the data files, and the wheel, which is separately
# referenced as `../public/wheels/...` relative to the page. One `public/` at the root satisfies
# all of them. Splitting them is what produced "no stored answer, skipping" in the browser with
# the module importing and the checker running perfectly well.
#
# marimo builds the `tn23015` wheel itself from the local module the notebooks import. It does not
# follow symlinks, which is why `marimo-notebooks/tn23015.py` is a real file.
#
# If files under `public/` go missing after a deploy while everything else is there, suspect a
# **truncated upload** before suspecting the layout: `public` sorts after `assets` and after the
# numbered chapter directories, so it is the tail of the walk and the first casualty of an
# interrupted transfer. That signature was once misread here as Curvenote dropping the directory
# for its name; it was not, and renaming it away from marimo's own convention bought nothing.
#
# Solutions are absent, not hidden: the notebook source sits in `index.html` in plain view.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=marimo-apps
STAGE=_marimo_src

rm -rf "$STAGE" "$OUT"
mkdir -p "$STAGE" "$OUT/public/wheels"
.venv/bin/python scripts/make_student_notebooks.py --out "$STAGE" >/dev/null
cp marimo-notebooks/tn23015.py "$STAGE/"

for nb in "$STAGE"/[01][0-9].*.py; do
  slug=$(basename "$nb" .py)
  .venv/bin/marimo export html-wasm "$nb" -o "$OUT/$slug" --mode edit --force >/dev/null
  rm -f "$OUT/$slug/CLAUDE.md"          # marimo's own, not ours, and not for students

  if [ ! -d "$OUT/assets" ]; then
    mv "$OUT/$slug/assets" "$OUT/assets"
  else
    diff -rq "$OUT/assets" "$OUT/$slug/assets" >/dev/null \
      || { echo "assets differ for $slug -- the shared copy is not safe"; exit 1; }
    rm -rf "$OUT/$slug/assets"
  fi
  sed -i '' 's|"\./assets/|"../assets/|g' "$OUT/$slug/index.html"

  for whl in "$OUT/$slug"/public/wheels/*.whl; do
    dest="$OUT/public/wheels/$(basename "$whl")"
    if [ -e "$dest" ] && ! cmp -s "$whl" "$dest"; then
      echo "wheel differs for $slug -- the shared copy is not safe"; exit 1
    fi
    mv -f "$whl" "$dest"
  done
  rm -rf "$OUT/$slug/public"
  echo "  $OUT/$slug"
done

# All eleven chapters at once: 1.1 MB of answers and 4.9 MB of data, shared rather than staged
# per chapter, because every notebook now resolves them from the same root.
cp -r answers "$OUT/public/answers"
cp -r data "$OUT/public/data"
rm -rf "$STAGE"

# marimo ships its whole editor: CodeMirror grammars for two dozen languages, every Mermaid
# diagram type, a SQL parser, Vega, cytoscape, a terminal. A Python notebook touches none of it.
# `scripts/trace_marimo_assets.py` runs every chapter in a headless browser and records what is
# actually fetched -- measured rather than guessed from filenames -- and the rest goes: 728 files
# and 28 MB become 369 and 13 MB.
#
# **Knowingly sacrificed.** The trace cannot click what only appears once the kernel is up, so the
# side panels (packages, dependency graph, logs, tracing, scratchpad, snippets, terminal, chat)
# and the app-view slides are not in the keep list, and their buttons do nothing. Confirmed in a
# real browser: editing, running and grading all work; those panels do not. They are instructor
# and developer tools, and restoring them means restoring their dependency closures too -- the
# terminal wants xterm, the dependency graph wants cytoscape at 428 KB -- which is the weight this
# is trying to shed. If they are ever wanted, add the ~25 `*-panel-*` chunks *and* whatever they
# import, or re-trace with the panels open.
KEEP=scripts/marimo_assets_used.txt
if [ -f "$KEEP" ]; then
  before=$(ls "$OUT/assets" | wc -l | tr -d ' ')
  ( cd "$OUT/assets" && ls > /tmp/.marimo_have.txt \
    && comm -23 <(sort /tmp/.marimo_have.txt) <(sort "$OLDPWD/$KEEP") | while read -r f; do
         rm -f -- "$f"
       done )
  echo "  assets: $before -> $(ls "$OUT/assets" | wc -l | tr -d ' ') files (unused chunks dropped)"
else
  echo "  $KEEP missing -- keeping all assets; run scripts/trace_marimo_assets.py to slim them"
fi

echo
echo "total: $(du -sh "$OUT" | cut -f1), $(find "$OUT" -type f | wc -l | tr -d ' ') files"
echo "serve with: python -m http.server --directory $OUT   then open /<chapter>/"
