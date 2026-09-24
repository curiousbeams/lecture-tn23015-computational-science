#!/usr/bin/env bash
# Build the JupyterLite that the site serves at /jupyter-lite/.
#
# Not committed -- 21 MB and 526 files, regenerable in about a minute. Run this before
# `curvenote submit`, since myst.yml's `static_files` copies the result into the build.
#
# `--contents` needs jupyter-server present or the build fails at the very last step with
# "jupyter-server is not installed. You cannot add custom content to jupyterlite."
set -euo pipefail
cd "$(dirname "$0")/.."

# See the note in build_marimo_apps.sh: the site build never deletes static_files it copied
# before, so the stale copy goes here too.
rm -rf _build/site/public/jupyter-lite
rm -rf _jupyter_lite_src jupyter-lite .jupyterlite.doit.db
mkdir -p _jupyter_lite_src
cp jupyter-notebooks/*.ipynb _jupyter_lite_src/
cp packages/tn23015.py _jupyter_lite_src/
cp -r answers _jupyter_lite_src/answers
# 4.8 MB, and it means no reader's exercise depends on GitHub being reachable
cp -r data _jupyter_lite_src/data

uv run --no-project \
  --with jupyterlite-core --with jupyterlite-pyodide-kernel --with jupyter-server \
  jupyter lite build --contents _jupyter_lite_src --output-dir jupyter-lite \
  --apps lab --no-unused-shared-packages --no-sourcemaps

# 48 MB of the 69 MB a plain build produces is source maps for JupyterLab itself, which no
# reader needs. Dropping them is the difference between 21 MB and 69 MB in the deploy.
find jupyter-lite -name "*.map" -type f -delete
du -sh jupyter-lite
