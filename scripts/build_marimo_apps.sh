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

echo
echo "total: $(du -sh "$OUT" | cut -f1), $(find "$OUT" -type f | wc -l | tr -d ' ') files"
echo "serve with: python -m http.server --directory $OUT   then open /<chapter>/"
