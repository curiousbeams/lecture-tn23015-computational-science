# TN23015 — Computational Science

An interactive computational science textbook: numerical methods for physics, worked in the
browser. Built with [MyST](https://mystmd.org) (Jupyter Book 2) and
[marimo](https://marimo.io), so every code cell is live and editable with no server and nothing
to install.

Taught in Q2 2026–2027 at TU Delft by Georgios Varnavides (Imaging Physics) and
Danny Lathouwers (Radiation Science and Technology).

Adapted under CC BY 4.0 from *Computational Science: Interactive Textbook* by Gary Steele,
Jeroen Kalkman, Thomas Spriggs and Eliska Greplova, written for TN2513.

## Running it locally

```bash
uv sync
uv run myst start
```

## Layout

| | |
|---|---|
| `NN.<topic>.md` | one chapter each, in reading order |
| `answers/` | stored answer keys, one JSON per chapter |
| `data/` | the two datasets the exercises load |
| `figures/` | images referenced by the chapters |
| `scripts/` | the Jupyter Book 1 → MyST converter, and its notes |
| `static/custom.css` | site styling |

The chapters are generated files, converted once from the original book's jupytext sources, and
are now edited directly — **`scripts/convert_chapter.py` is frozen and re-running it would
discard those edits.** It is kept because `scripts/NOTES.md` beside it is the record of how the
port works and why: marimo's one-definition-per-global rule, how unfinished exercises are held
back, how answers are checked, and the browser-level constraints behind each decision. Read it
before changing anything structural in the chapters.

## How an exercise works

Blanks start as `None` and the code that would use them sits behind `given(...)`, so an unfinished
exercise renders a note saying what it is waiting for instead of a traceback. Filling a blank in
lets every cell downstream of it run, which is marimo's reactivity doing the work. Each exercise
ends in a check that compares against the stored key and re-runs itself as the answer changes.

`00b.about.md` explains the same thing from the student's side.

## Data files

`data/` is fetched over the network at runtime — there is no filesystem in the browser — from
this repository's `main` branch via `raw.githubusercontent.com`. **This is why the repository is
public**: raw.githubusercontent does not serve a private repo without a token. Moving the repo
to private, or renaming it, means updating `DATA_URL` in each chapter's `{marimo-config}` header.
