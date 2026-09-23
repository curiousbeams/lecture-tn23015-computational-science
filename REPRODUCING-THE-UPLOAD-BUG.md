# Reproducing the truncated `static_files` upload

Notes for Curvenote. The two directories involved, `jupyter-lite/` and `marimo-apps/`, are
generated and gitignored, so a clone alone will not show the problem — they have to be built
first. Everything below runs from a fresh checkout on macOS or Linux and needs only
[`uv`](https://docs.astral.sh/uv/) plus network access.

## The symptom

`curvenote submit` reports success. A large, **contiguous** tail of `static_files` is then missing
from `pub.curvenote.com/<cdnKey>/public/`, returning 404 while everything before it returns 200.
Nothing in the CLI output indicates a problem.

Measured twice, on deploys of very different size:

| static files submitted | reachable afterwards | missing |
|---|---|---|
| 1415 | **954** | 461 |
| 1056 | **954** | 102 |

Both landed *exactly* 954 files, which is why we think it is a count limit rather than bytes or
anything about the content. In each case the loss is one unbroken run in sort order — in the
second, everything from `marimo-apps/assets/select-CPo-KTTe.js` to the end of the list, which
sweeps up marimo's web worker, its wheel, and all of `marimo-apps/public/`.

There is a second effect that makes it sticky: the **next** submission reports

```
🔬 Preparing to upload - found 1512 files
📤 Staging complete - 49/1512 files need to be uploaded.
```

so the files lost to the first upload are treated as already stored and never retried. Re-submitting
does not heal it; clearing the cache on your side did not either — it truncated again at 954.

## Build the two bundles

```bash
git clone https://github.com/curiousbeams/lecture-tn23015-computational-science
cd lecture-tn23015-computational-science
uv sync

bash scripts/build_jupyter_lite.sh    # -> jupyter-lite/   552 files,  27 MB
bash scripts/build_marimo_apps.sh     # -> marimo-apps/    504 files,  21 MB
```

Both are ordinary static bundles: JupyterLite as produced by `jupyter lite build`, and eleven
`marimo export html-wasm` exports sharing one `assets/` directory. `myst.yml` lists them under
`project.static_files`. Neither script needs the project's own content, so if it is easier to test
with something synthetic, ~1100 small files in a `static_files` directory should do it.

The marimo build takes a few minutes (eleven WASM exports). If `scripts/marimo_assets_used.txt` is
present it also drops marimo's unused lazy chunks, 728 assets down to 369 — that slimming is what
produced the second row of the table above.

## Submit and check

```bash
curvenote submit curious-beams --kind lecture --collection lectures

.venv/bin/python scripts/check_deploy.py          # ~130-file sample, seconds
.venv/bin/python scripts/check_deploy.py --all    # all of them, a minute or two
```

`check_deploy.py` reads the cdnKey from `_build/logs/curvenote.submit.json`
(`job.results.cdnKey`) and asks the CDN for each file the build produced. It samples in sort order
by default, since the loss is contiguous. Expected output today:

```
954 present, 102 missing
```

To see the boundary rather than a count, `--all` prints every missing path; they are consecutive.

## Notes that may or may not matter

* Nothing depends on the *names* involved. An earlier theory that a nested directory called
  `public/` was being dropped turned out to be this same truncation seen through too small a
  sample.
* An upload was genuinely interrupted once, early on. The 954 figure has been stable across
  submissions since, including ones that completed without incident.
* `jupyter-lite/` sorts before `marimo-apps/` and is essentially always complete; the loss lands
  in whatever sorts last.
