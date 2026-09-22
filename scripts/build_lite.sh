#!/usr/bin/env bash
# Build the JupyterLite that the site serves at /lite/.
#
# Not committed -- 21 MB and 526 files, regenerable in about a minute. Run this before
# `curvenote submit`, since myst.yml's `static_files: [lite]` copies the result into the build.
#
# `--contents` needs jupyter-server present or the build fails at the very last step with
# "jupyter-server is not installed. You cannot add custom content to jupyterlite."
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf _lite_src lite .jupyterlite.doit.db
mkdir -p _lite_src
cp notebooks/*.ipynb _lite_src/ 2>/dev/null || true
cp packages/tn23015.py _lite_src/
cp -r answers _lite_src/answers

uv run --no-project \
  --with jupyterlite-core --with jupyterlite-pyodide-kernel --with jupyter-server \
  jupyter lite build --contents _lite_src --output-dir lite

# 48 MB of the 69 MB a plain build produces is source maps for JupyterLab itself, which no
# reader needs. Dropping them is the difference between 21 MB and 69 MB in the deploy.
find lite -name "*.map" -type f -delete
du -sh lite
