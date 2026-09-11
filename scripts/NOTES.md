# Porting notes: verified behaviour of mystmd 1.10.1 + jupyter-book-marimo 0.0.3

Findings from the smoke test (`_smoke.md`, since removed). All verified by building, not assumed.

## 1. Directive options MUST be single-line — YAML block scalars are broken

The plugin's own docs show:

````markdown
```{marimo-config}
:pyproject: |
  requires-python = ">=3.12"
  dependencies = ["numpy"]
```
````

**This fails** under mystmd 1.10.1. The `|` is passed through literally, so the plugin receives
TOML starting with `|` and dies with:

```
error: TOML parse error at line 1, column 2
1 | |
  |  ^  key with no value, expected `=`
```

Use single-line values instead, joining Python statements with `;`:

````markdown
```{marimo-config}
:pyproject: dependencies = ["numpy", "matplotlib"]
:header: import numpy as np; import marimo as mo; import matplotlib.pyplot as plt
```
````

This constraint applies to **every** multi-line directive option, not just these two.

## 2. Runtime errors do NOT fail the build

A cell raising `NameError` (an unfilled student stub) compiles fine; the traceback is captured
into the cell's output. Confirmed: `NameError` appears in the built `smoke.json`, and the page
still built.

So stubs only need to **parse**. They may raise at runtime. `:eval: false` is not needed.

## 3. Answer keys go inline as a marimo cell, not a fetched file

Only *options* are limited to one line — *cell bodies* can be arbitrarily long and multi-line.
So the answer key is defined as a plain global in a `{marimo}` cell:

```python
ANSWERS = {"answer_3_01_1": [...], ...}
```

This sidesteps the whole question of whether Pyodide/WASM can read a same-origin file, which was
the biggest open risk in the plan. Nothing is fetched at runtime.

## 4. Function-encapsulating solutions LOOKED right and was wrong — Rule 1 revised

`def _solution(): ...` does render its figure and does contribute no globals, exactly as the
plan predicted. But running the converted chapter revealed that **the chapters are linear
chains**: solution 2 reads `f` and `fp` from exercise 1, solution 5 reads `t`, `t_fwd` and
`fwd_derv` from solution 4. Hiding every solution binding inside a function severed that chain —
7 of 10 solutions in chapter 3 failed with `NameError` / `TypeError`.

It also destroyed the recovery path the original book depends on. In Jupyter Book 1 a stuck
student runs the solution cells in order and every global gets defined; with function wrapping,
running solution 1 defines nothing, so solution 2 still fails.

**Revised Rule 1: solutions keep their own global chain, namespaced with a `_sol` suffix.**
Every name a solution binds becomes `<name>_sol`, and reads of names bound by an *earlier*
solution are rewritten to match. Students keep the natural names in their own stubs, so the two
chains coexist under marimo's one-definition-per-global rule:

| | student chain | solution chain |
|---|---|---|
| exercise 1 | `f`, `x`, `y`, `answer_3_01_1` | `f_sol`, `x_sol`, `y_sol` |
| exercise 2 | reads `f`, `x` | reads `f_sol`, `x_sol` |

Renaming is done over Python **tokens**, not regex, so string literals (`label='f(x)'`) and
attribute names (`plt.plot`) are untouched.

Result: 10/10 solutions execute, and the chain demonstrably works — the converted page prints
`Forward: 0.031027  Error: -0.039624` from a solution that depends on two earlier ones.

## 5. `mo.stop` + `mo.ui.run_button` works

The gate renders its fallback markdown instead of the result, and no `MarimoStopError` leaks into
the output.

## 6. Underscore locals can be redefined across cells

Two cells both assigning `_x` compile without a multiple-definition error, as documented.

## 7. Gated exercise/solution syntax is required and works

`{exercise-start}` / `{exercise-end}` and `{solution-start}` / `{solution-end}` correctly wrap
`{marimo}` cells. The built AST shows an `exercise` node labelled `ex_3_01` and a `solution` node
with `class=dropdown`.

## Still unverified (needs a real browser)

- micropip cost for numpy + matplotlib + scipy on first page load, especially on mobile.
- Whether the editor, run button, and reactive re-execution behave in the deployed page.

Build cost is ~3.5 s per page with 6 marimo cells.

## 8. Every import must be hoisted into the page header

`import numpy as np` binds the global `np`. The source book re-imports numpy and matplotlib in
most cells, which marimo reads as many cells defining `np` — and that surfaces as an error on
the *setup* cell, which **does** fail the build (unlike an authored-cell error, see §2).

So `collect_imports` takes the union of every top-level import in the chapter, drops the ones
that no longer apply (`validate_answers`, `micropip`, `ipywidgets`, `IPython`), and joins them
into the single-line `:header:`; `strip_imports` removes them from the cells.

## 9. Markdown blocks must be split at the exercise markers

jupytext only breaks a block at a code fence, so prose and the following `**Exercise 1:**` text
arrive as one chunk. Gating the whole chunk wrapped the chapter's entire introduction inside
exercise 1, and swallowed each `**Self check:**` list into the *next* exercise. `split_markdown`
splits on both markers first.

## Verified results for chapter 3 (Numerical Differentiation)

- 45 marimo cells, 10 exercises, 10 dropdown solutions, 2 figures, 15 math blocks.
- Prose preserved: 3333 source words -> 3335 ported.
- Solutions: 10/10 execute. Answer bank, checker and buttons: all pass.
- Remaining failures are stubs (unfilled by design) and their dependent check cells; marimo does
  not run descendants of a failed cell, so these do not surface to the reader.
- Checker verified against correct answers, wrong values (element-wise diff), and wrong shape.
- Downsampled keys round-trip exactly and still reject a 10% perturbation.

---

# Round 2: fixes from testing the built page in a browser

Three problems only a real browser showed, all rooted in one difference from Jupyter Book 1:
**marimo runs every cell on page load.** JB1 never ran a cell until the reader clicked it, so an
unfilled stub was simply blank.

## 10. Unfilled stubs threw at the reader

Before typing anything the reader saw `NameError: name 'x' is not defined`, and the check cell
below it showed `Ancestor raised ... cell-4`.

Fix, in `add_placeholders`:

1. declare every blank up front as `None`, so the names exist;
2. insert an `mo.stop` guard immediately *before* the first statement that consumes a blank.

The guard sits after the region the student fills in, so it passes as soon as real values are
assigned. `mo.stop` also leaves descendants un-run rather than failed, which is what silences the
check cell. Chapter 3 now has 9 gated cells and **0 failing stubs**.

## 11. Blanks are marked by commented-out assignments, not by being undefined

Detecting blanks as "names this cell reads but never binds" missed the important case: exercise 4
wants its own `h`, but exercise 3 already bound `h = 0.5`, so `h` *was* defined and the stub
silently computed against a float — `AttributeError: 'float' object has no attribute 'copy'`.

The book's own convention is `# h = ...`, so `commented_blanks()` reads that instead. This fixed
three separate failures at once.

## 12. Placeholders manufactured the very collisions they were meant to avoid

Declaring `t = None` in every cell that *reads* `t` made five cells define `t`. Placeholders are
now only added for names no earlier cell owns (`page_globals`).

## 13. A flat `_sol` suffix was not enough — versioning is required

The browser reported `CELL NOT RUN — x_sol was also defined by cell-19`: several solutions rebind
the same name. Both chains now use static single assignment — `x_sol1`, `x_sol5` for solutions,
and for students the first binder keeps the natural name while later rebindings become `t_2`.

`i`, `j`, `k`, `n` had to come *out* of `PROTECTED`: a top-level `for i in ...` binds a global, so
two solutions both owning `i` is a collision.

## 14. Solutions need `:echo: true`

`:editor: false` hides the editor, and `:echo:` defaults to false — so the solution dropdown
opened on an output with no code at all. Solutions are now `:echo: true` + `:editor: false`.

## 15. Never rebuild source with `tokenize.untokenize`

It reflows whitespace (`x =y =None`, `plt .plot (`) and re-indents comments — unacceptable in
code students read and edit. `_retoken` now uses the token stream only to *locate* names and
splices the edits into the original text back-to-front. It also renames the name inside a
commented-out assignment, so the `# h_3 = ...` hint agrees with the code.

## A structural check the linear sweep cannot do

`duplicate_globals()` in `validate_page.py` reports any global bound by more than one cell. This
is the class of bug that shows up only in the browser as "CELL NOT RUN", because it never raises
during a linear execution. Run it on every converted chapter.

---

# Round 3: whole-book conversion, and the object-oriented matplotlib rewrite

## 16. Plotting is now `fig, ax`, and that *is* the fix for the stray figures

Every solution appeared to produce a figure because matplotlib's registry is global across cells
and `plt.gca()` returned whatever was open. Diffing figure numbers does not help either: a cell
calling `plt.plot` draws onto an already-open figure and creates no new number.

`oo_plots.py` rewrites the pyplot state machine into the taught idiom instead. Plotting
statements move into a cell-local `def _plot()` that returns `ax` (`fig` for multi-panel), so
`fig`/`ax` never become globals -- with ~76 plotting cells they would otherwise be ~76
collisions. Data assignments stay at the top level, keeping the chain intact.

Handled mechanically: `plt.xlabel` -> `ax.set_xlabel`; `plt.subplot(121)` -> `ax = axs[0]` under
one `fig, axs = plt.subplots(1, 2, ...)`; a bare `plt.colorbar()` captures its mappable
(`_im = ax.imshow(...)`; `fig.colorbar(_im)`); `plt.clim` -> `_im.set_clim`; `plt.show()`
dropped. Inline code spans in the prose are converted too, or the instructions would contradict
the code.

## 17. Renaming has to be scope- and position-aware

Two bugs, both found by running the converted pages:

* **Scope.** Versioning renamed function *parameters*: `def update(zoom=1000)` became
  `def update(zoom_sol6=1000)`. Excluding the name cell-wide was worse -- the call site stopped
  being renamed too, so a solution called the student's empty stub `f` and got `None - None`.
  `local_scopes()` now limits the exclusion to the function's own byte range.
* **Position.** ODE2's fourth solution reads `t` on one line and rebinds it on the next
  (`t_eval=t` ... `t = sol.t`). A uniform rename produced `t_eval=t_sol4` one line before
  `t_sol4` existed. `first_bindings()` makes reads before the first binding resolve to the
  previous version.

## 18. An unfilled `while` loop hangs the build *and* the browser

PDE1 ships `while delta_max > target_accuracy:` with the body commented out. Filling the body
with `...` made it spin forever -- the build never finished. The `None` guard does not catch it,
because the cell assigns `delta_max = 1` further down.

`has_unfinished_loop()` flags a `while` whose body never assigns any name in its condition and
has no `break`; such cells get an unconditional `mo.stop` the student deletes. One cell in the
book, and it would have hung a reader's tab exactly as it hung the build.

## 19. The answer bank is Python source, not JSON

`json.dumps` writes `true`/`false`/`null`, which are not Python literals, so the downsampled
entries' boolean flag became `NameError: name 'true' is not defined`. Emitted with `repr()` now.

## 20. Hoisted import names must be parsed, not split

`from numpy import array,empty` has no space after the comma, so `.split()[-1]` yielded the token
`array,empty`. `empty` then looked undefined, earned a `None` placeholder, and collided with the
import: `MultipleDefinitionError(name='empty')`. `imported_names()` parses instead.

## 21. Four failures were pre-existing bugs in the source book

Verified by running the *original* solution cells unmodified -- they fail identically there:

* `sol.t_events[0]` is the array of event times, used as a scalar (ODE2, three cells). Printing
  it raises "only 0-dimensional arrays can be converted to Python scalars"; assigning it into
  `tf1[i]` raises "setting an array element with a sequence". The book already uses the correct
  `sol.t_events[0][0]` elsewhere.
* `label=['mode 1: omega^2=', str(omega1**2)]` -- matplotlib rejects a list label for a single
  dataset (Linear_algebra).

Both are in `CONTENT_FIXES`, applied before any transform. Also corrected: `fix, ax =
plt.subplots(...)`, a typo in Fourier_transforms_2.

## 22. `%%capture` had to go

Four PDE2 cells used it to hide a FuncAnimation's static frame. It is not valid Python, so those
cells never parsed and every transform skipped them. marimo has no cell magics; the line is
dropped.

## 23. The one `ipywidgets` exercise is now marimo sliders

`SPLIT_CELLS` turns FT2's `interact(update, ...)` into two cells -- `mo.ui.slider` definitions,
then the plot that reads `.value` -- because a marimo UI element is only reactive when it is
defined in one cell and read in another. The original text apologises for its own widget ("the
update is not super-fast"), so this is a straight improvement.

## Data files

`velocities.dat` and `data.dat` live at the repo root, where the exercises' bare `np.loadtxt`
paths resolve. **Open question:** under Pyodide those paths will not resolve in the reader's
browser -- the two exercises that load data still need a fetch-based solution.

## Build cost

A clean build runs every cell in a real Python environment: about 5 minutes for the book, and
PDE1's pure-Python relaxation loops dominate. `validate_page.py` takes a `budget` per cell
(default 20 s) so a linear sweep does not look like a hang.

## 24. Page payload has a hard ceiling

Inlining PDE1's answer bank produced a 1.48 MB single line and mystmd refused to read the page:
`SyntaxError: Unterminated string in JSON at position 1114112` (~1 MiB). Two changes:

* `python_literal()` wraps the literal at comma boundaries (newlines inside brackets are implicit
  line joins), keeping it compact -- `pprint.pformat` fixes line length but more than doubles the
  payload in indentation.
* the downsample threshold dropped to 4000 elements (target 2500). PDE1's 101x101 grids sat just
  under the old 20k limit and so were stored in full.

**121.6 MB -> 1.14 MB**, largest page now 0.45 MB.

## 25. One `{solution}` per exercise, and only for labels that exist

Several exercises ship two solution cells, so a second `:::{solution-start} ex_6_05` was a
duplicate cross-reference. Extra solutions now render as a plain `{admonition} Solution` dropdown,
as do solutions whose exercise never existed.

## 26. A self check is the bullet list, nothing more

`split_markdown` gave the `**Self check:**` segment everything up to the next exercise marker, so
the admonition swallowed 64 lines of Linear_algebra -- a heading, a figure, display math and the
next exercise's set-up -- which also stopped `ex_6_05` registering its label. `_leading_list()`
now takes only the list and returns the rest as prose.

## Final state

13 pages, **zero warnings, zero errors**, 44 s incremental build. All 11 chapters pass
`validate_page.py`: no failing solutions, no duplicate globals, stubs gated rather than throwing.

---

# Round 4: cell options, and what islands cannot do

## 27. Measured semantics of the marimo cell options

Probed by building a page with each variant and reading `data-reactive` and the error mime out of
the compiled island HTML:

| options | reactive | build-time error shown | editor |
|---|---|---|---|
| *(plain)* | **true** | yes -- `NameError` baked into the page | yes |
| `:eval: false` | **true** | no | yes |
| `:disabled: true` | false | no | yes |
| `:unparsable: true` | false | yes -- the `IndentationError` | yes |
| `:unparsable: true` + `:server-output: false` | false | no | yes |
| `:error: false` | — | **fails the build** | — |

Two things worth knowing:

* **`:error: false` does not hide the error, it makes the error fatal.** The docs' wording
  ("render marimo error output instead of failing on error") reads the other way round at a
  glance.
* **`:disabled:` and `:unparsable:` both produce `data-reactive="false"`.** That is the whole
  point for `:unparsable:` -- code that cannot be parsed cannot join the graph -- but it likely
  means the reader cannot run those cells either. Unverified in a browser.

**Stubs now use `:eval: false`**: no build-time execution, so nothing is baked into the page, and
the island stays reactive so the reader can still edit and run. `:unparsable: true` +
`:server-output: false` is emitted as a fallback for any stub that does not parse (none currently
do, since `normalise_stub` repairs them -- keeping them parsable is what preserves reactivity).

This also removed every `NameError` from the built chapter 1: previously 15, now 0.

## 28. Cmd/Ctrl+Enter cannot work in an island

The islands bundle simply does not ship the hotkey system. Counting occurrences in
`@marimo-team/islands@0.24.0/dist/main.js` against marimo's full app bundle:

| token | islands | full app |
|---|---:|---:|
| `Mod-Enter` | 0 | 2 |
| `cell.run` | 0 | 15 |
| `hotkey` | 0 | 76 |

`sendRun` *is* present (3 hits), so islands can run a cell -- via its run button, not a shortcut.
`defaultKeymap` (1 hit) is CodeMirror's editing keymap: arrows, indent, undo. So the shortcut
table in marimo's docs applies to the marimo app, not to an embedded island. Worth an upstream
issue; until then the docs in `00b.about.md` tell readers to use the run button.

## 29. Fences nest by length

Folding a `:::{hint}` into a `:::{tip} Self check` silently mis-parsed -- MyST nests by fence
length, so the outer one has to be longer. `fence_for()` computes it from the body.

## 30. Each panel needs its own colorbar mappable

`fig.colorbar(mappable)` steals space from *that mappable's* axes, so reusing one `_im` across a
three-panel figure put all three colorbars on the left-hand axis. Mappables are now captured
sequentially (`_im1`, `_im2`, `_im3`) and each bare `plt.colorbar()` pairs with the one most
recently drawn.

## 31. A self check keeps its trailing question

Several exercises end with "What do you see in the plot?" or a parenthetical hint that belongs
with the check. `_leading_list()` now keeps consuming plain paragraphs after the bullet list and
stops at the first structural element (heading, directive, display math, image, code fence).
Parenthetical hints anywhere become `:::{hint}` admonitions.

---

# Round 5: what actually works for answer checking

Three candidates were tried. Only the third survives.

## 32. `:eval: false` removes the cell from the page

Measured wrongly the first time: the compiled payload *contains* a `marimo-code-editor` node, so a
static probe says "editor: yes". In the browser the cell does not render at all -- excluded from
execution means excluded from the hydrated app. The probe table was wrong on that row; a browser
is the only authority here.

Stubs are back to plain `:editor: true` with an `mo.stop` guard. Of the option matrix, **plain is
the only variant that yields an editable, reactive cell**:

| options | renders an editable cell? |
|---|---|
| *(plain)* | yes |
| `:eval: false` | **no** |
| `:disabled: true` | reactive=false |
| `:unparsable: true` | reactive=false |

## 33. marimo's pytest integration works in an island, but is invisible

Confirmed in a browser: test cells *do* run under the WASM kernel and pytest reports pass/fail.
But `attempt_pytest` ends with `sys.stdout.write(result.output)`, and in an island stdout goes to
the **browser console**, not the cell output. A student would never see it. There is no authoring
knob to redirect it, and the report is the full pytest transcript besides.

Verdict: unusable for this book. Requires `pytest` in the page dependencies too, and fails
silently without it (`except ImportError: pass`).

## 34. mograder: right pattern, wrong dependency

[mograder](https://jameskermode.github.io/mograder/) is an nbgrader-equivalent for marimo. Its
student-facing API is exactly the shape needed:

```python
def check(label, checks) -> mo.Html:      # returns mo.callout(..., kind="success"|"danger"|"warn")
def hint(*hints) -> mo.Html:              # mo.accordion of progressive hints
```

**Returning an `mo.Html` is the crucial difference from pytest** -- it renders as the cell's
output, which is what an island can show.

It is WASM-safe: `mograder/runtime.py` imports only `json`, `os`, `re` and `marimo`, and
`_write_sidecar` is a no-op unless `MOGRADER_SIDECAR_PATH` is set, so nothing touches the
filesystem in a browser. All its dependencies (click, httpx, requests, websockets) publish
pure-python wheels, so micropip *could* install it.

**Not adopted as a dependency**, because the part we need is ~40 lines and everything else is
instructor-side infrastructure that a static site cannot use: `autograde` runs submissions in
sandboxed subprocesses, the gradebook is SQLite, and there is a hub server and Moodle
integration. Its `generate` step also assumes it owns notebook authoring, which collides with
this converter. Pulling five packages into every student's WASM download for two functions is a
bad trade.

Worth revisiting if the course ever wants real submission and grading.

## 35. The check is now a reactive callout

`check_answers()` returns `mo.callout(...)` with three kinds, following mograder:

* **success** -- "Correct."
* **danger** -- "Not quite yet.", with the element-wise diff
* **warn** -- "Waiting for your code: replace the `None` placeholders above."

The run button is gone: two cells per exercise became one, and the check re-runs by itself when
the answer changes. Premature checking is already prevented by the stub's `mo.stop`, since marimo
does not run a stopped cell's descendants -- that is what the `ancestor-stopped` outputs are.

## 36. `mo.stop` in a stub is a dead end -- the guard has to be inside a function

`mo.stop` propagates **structurally**, not as an exception: marimo refuses to run *any* descendant
of a stopped cell, forever, and the descendant renders nothing at all -- the reader gets a blank
cell and a console line:

```
{"type":"ancestor-stopped","msg":"This cell wasn't run because an ancestor was stopped with `mo.stop`"}
```

Pressing play on the check cell does nothing, because its ancestor is stopped. Worse, the guard
sat *above* the `answer_* = ...` lines, so the answers were never defined either.

The fix is to stop stopping. A stub now:

1. declares its blanks as `None`;
2. runs to completion, **always defining its `answer_*` variables**;
3. guards only the statements that *display* a blank -- plots and prints -- by moving them into
   the cell-local display function behind an early return:

```python
def _plot():
    if any(_v is None for _v in (x, y, y_prime)):
        return mo.md("*Fill in the code in this cell to see its output.*")
    fig, ax = plt.subplots()
    ...
    return ax

_plot()
```

Assignments stay outside the guard on purpose: that is what keeps the answers defined, so the
check cell below always runs and can show its amber "waiting for your code" callout.

Book-wide, `ancestor-stopped` fell from 85 to 2 -- and the two that remain are PDE1's genuinely
non-terminating loop, which must not run.

## 37. A stub needs an output, or it has no play button

Two failures with the same cause. `answer_3_06_1 = h.copy()` raises `AttributeError` when `h` is
`None`, so the cell died before producing anything -- and **a marimo island with no output gives
the reader no play button**, so the cell could not be run at all. Exercise 1 had the same problem
for a different reason: all of its plotting is commented out in the source, so there was nothing
to render even when the cell succeeded.

Both fixed:

* the placeholder is now `UNSET = np.array(np.nan)`, defined in the page header, instead of
  `None`. The stubs *operate* on their blanks -- `h.copy()`, `np.copy(x)`, `"%f" % err` -- and a
  0-d NaN array survives all of them while `None` raises on every one;
* the display function is emitted for **every** stub that has blanks, even one with no plotting,
  so an unfilled stub always renders "Fill in the code in this cell to see its output."

`is_unanswered()` recognises the sentinel by identity, and a copy of it by being a 0-d NaN.

## 38. Statements must be split by line range, not `ast.get_source_segment`

Reassembling the cell from AST segments silently dropped every comment -- and this book's
scaffolding *is* comments (`# x = ....`, `# Now the plot`). Cells are now split on statement line
ranges, so comments travel with the statement that follows them.

## 39. Two renaming traps found by running the pages

* **Keyword arguments.** `ax.imshow(..., vmax=vmax)` had its *parameter* name rewritten, giving
  `AxesImage.set() got an unexpected keyword argument 'vmax_sol8'`. Now skipped.
* **...but only inside brackets.** The first fix broke tuple unpacking: in `eigA, eigvA = ...`
  the second target is also preceded by `,` and followed by `=`, so it stopped being renamed and
  `eigvA_sol6` vanished. `is_kwarg()` now requires bracket depth > 0.

## 40. Split rules run before renaming

`SPLIT_CELLS` matched `interact(update,` in both the stub and the solution, because SSA renaming
happens later -- at split time both still read `update`. The rules are now keyed on
`is_solution` as well as the marker.

## Known gap in `validate_page.py`

It executes cells linearly in one namespace with a stubbed `mo`; marimo executes a dependency
graph. A page can pass the validator and still show errors in the built site, so **the build's
error counts are the authority**, and a browser is the authority over both.

## 41. `preview()` replaces the per-stub guard

Every stub carried four lines of identical guard. It is now one call, with the helper living in
the page's inlined runtime beside `check_answers`:

```python
def preview(*args):
    fn = args[0] if args and callable(args[0]) else None
    blanks = args[1:] if fn is not None else args
    if any(b is UNSET for b in blanks):
        return mo.md("*Fill in the code in this cell to see its output.*")
    return fn() if fn is not None else None
```

`preview(_plot, x, y, y_prime)` when the cell draws something, `preview(x, y, y_prime)` when it
only needs an output so the island has a play button.

## 42. Unanswered detection has to see through containers

`answer_3_02_1 = (yd_forward, error_forward)` is a *tuple* of sentinels, and `np.asarray` turns
that into an ordinary `(2,)` float array of NaN -- identity is gone, so the answer looked real,
was compared, and the reader got a red "incorrect values" callout before typing anything.
`is_unanswered()` now recurses into tuples/lists and treats any all-NaN array as unanswered.

## Open: re-running a cell in an island

Reported from the browser: after a cell is edited and run once, it cannot be run again. Not
reproducible outside a browser. What the bundle shows: islands ship `sendRun` and track `stale`
per cell, and there is an `isEditable` flag, but the code is minified past useful reading. This
looks like an upstream islands limitation rather than something the page controls -- it needs an
issue against `@marimo-team/islands`, since "edit, run, realise the mistake, try again" is the
core loop of every exercise in this book.

## 43. THE RULE: a cell with no build-time output is dead forever

Confirmed in a browser by isolating it (`_rerun.md`). Cells A, B, C, D and F -- plain, imports,
plot output, downstream, and slider-driven -- all re-run fine. **E, the cell with no output, has
no play button; and editing it to add `e` as a last expression changes nothing, because without a
play button it can never be run, so the edit never takes effect.**

So an island cell must produce output *at build time*, or it is inert. Editing cannot rescue it.

This was the cause of "I can't re-evaluate it again": `preview(x, y, y_prime)` returned `None`
once the blanks were filled, the output vanished, and the play button went with it. The cell
worked exactly once.

`preview()` therefore always returns something visible:

| state | output |
|---|---|
| any blank still `UNSET` | "Fill in the code in this cell to see its output." |
| display function returned a plot | the plot |
| otherwise | `Set \`x\` shape (100,), \`h\` = 0.5` |

The last row also covers print-only cells: `print()` alone is *not* an output here, since stdout
in an island goes to the browser console (see §33).

Blanks are passed by keyword -- `preview(_plot, x=x, y=y)` -- so the summary can name them, which
doubles as feedback before the answer check runs.

## 44. Scaffolding comments belong only in stubs

`# ...` filler is dropped everywhere: `normalise_stub` already writes a real `...`, so
`def f(x): ...` says it better. Commented-out blanks (`# yd_analytical = `, `# fwd_derv =
np.zeros(_____)`) are dropped from **solutions**, where they sat directly above the real answer
and had even been SSA-renamed into nonsense (`# yd_analytical_sol2 = `). They stay in stubs,
where they are the instructions.

## 45. Errors are recoverable; `mo.stop` is not

Worth stating plainly, because it changes what "good" looks like. A cell that *raises* still
renders its error, still has a play button, and once the student fixes it every dependent cell
re-runs. A cell stopped with `mo.stop` is dead for good, and so is everything downstream.

So residual errors in an unfilled stub are a cosmetic problem, not a functional one. The
sentinel exists to keep the page tidy on first load, not to make errors impossible.

## 46. Choosing the sentinel

`UNSET` is `np.full((2, 2), np.nan)`. The stubs operate on their blanks, and this shape survives
the most of it:

| operation | `None` | 0-d NaN | 2x2 NaN |
|---|---|---|---|
| `h.copy()`, `np.copy(x)` | ✗ | ✓ | ✓ |
| `len(x)`, `x.shape[0]` | ✗ | ✗ | ✓ |
| `x[i]`, `x[i, j]` | ✗ | ✗ | ✓ |
| `a, b = x` | ✗ | ✗ | ✓ |
| `"%f" % x` | ✗ | ✓ | ✗ |

The formatting row does not matter: `print` statements live inside `preview()`'s guard and do not
run while a blank is unset.

A stub *function* now returns the sentinel too (`def low_pass(...): return UNSET` rather than
`...`), and `stub_call_results()` marks anything assigned from calling one as a blank. Without
that, `vfilt = low_pass(v, 5, dt)` was silently `None` and the plot below it raised
"x, y, and format string must not be None" -- FT2's only errors.

Book-wide first-load errors: 43 -> 39, with FT1 10 -> 6 and FT2 4 -> 0.

## 47. Reference links

Raw URLs the source scattered inline are now proper links: Wikipedia via the `wiki:` role
(`[](wiki:Finite_difference)` renders the page title; anchors are spelled out), and numpy moved
off `docs.scipy.org` to `numpy.org/doc/stable` with the function name as link text.

Ordering matters: `fix_links` has to run *after* `ANCHOR_RE`, because most of these are raw
`<a href=...>` in the source and there is no markdown link to rewrite until that conversion has
happened.

## 48. Setup cells are not exercises

The chapter-opening cell only sets `plt.rcParams`, so it gets `:editor: false` -- there is nothing
to edit -- and `plt.rcParams` is classified as configuration rather than display, so it is no
longer swept into `_plot()`.

## 49. Loops do not create a scope -- the collision check was missing most collisions

`bound_names()` only walked `tree.body`, so a name assigned inside `while ...:` or `for ...:` was
invisible to both the versioning pass and `duplicate_globals`. Python binds those at cell scope
and so does marimo, which then refused to run the cell.

This is what broke NI exercise 2.3: its solution assigns `integral` inside a `while` loop, the
stub assigns `integral` too, marimo saw two definitions, neither cell ran, and the check cell
reported `NameError: answer_4_03_1`.

`bound_names()` now recurses through control flow and stops at function/class bodies (which *do*
introduce a scope). That surfaced real collisions in seven chapters that had been reported clean,
and clearing them took the book from 39 first-load errors to 26 -- NI, LA, ODE1, PDE1 and
root-finding all to zero.

**Loop counters are underscored, not versioned.** PDE1 binds `i` and `j` in six cells each;
versioning would have produced `for i_5 in range(M)`. `loop_only_names()` finds names bound
*solely* as `for` targets and makes them cell-local instead, which is both idiomatic and what a
reader expects of a counter.

## 50. Data files are fetched, not read

There is no filesystem in the browser, so `np.loadtxt("velocities.dat")` could never work there.
`load_data()` fetches from the original book's repository under Pyodide and falls back to the
local copy at build time:

```python
def load_data(path, **kwargs):
    try:
        from pyodide.http import open_url      # only exists under Pyodide
    except ImportError:
        return np.loadtxt(path.rsplit("/", 1)[-1], **kwargs)
    return np.loadtxt(open_url(DATA_URL + path), **kwargs)
```

`DATA_URL` points at raw.githubusercontent.com for TUDelft-books/Computational-Science-Interactive-Textbook.
**TODO: repoint at our own repository once this port is pushed.**

## Build-time note

The plugin's per-page compile timeout is 300 s and is configurable:
`JUPYTER_BOOK_MARIMO_UV_TIMEOUT_SECONDS`. A run where every page reported 3-4 minutes turned out
to be machine contention (a `myst start` competing with 11 parallel page compiles), not the
content -- the same tree rebuilt in 46 s once the server was stopped.

## 51. `print()` output has to be captured explicitly

`:server-output:` is on by default and *does* bake the build-time output into the island -- but
marimo's island build never captures stdout, so for a cell whose only result was a `print` there
was nothing to bake. Many solutions rendered blank, and with no output they had no play button
either, so a reader could neither see nor produce the result.

`:eval:`/`:server-output:` are not the missing switch. The fix is to capture stdout ourselves,
using marimo's own `mo.capture_stdout()`:

```python
def show(fn):
    with mo.capture_stdout() as out:
        value = fn()
    return shown(out.getvalue(), value)     # printed text, the figure, or both stacked
```

A standalone top-level `print(...)` is now classified as a *display* statement, so it moves into
the cell's display function alongside the plotting and is captured there. `preview()` does the
same for student cells. Solutions end on `show(_plot)` rather than `_plot()`.

Known limit: a `print` **inside a loop that also assigns** cannot move (the loop has to stay at
top level to keep its bindings global), so that output is still lost. It is debug chatter in
every case in this book.

## 52. Guard: every emitted cell must parse

The inlined runtime is a Python string inside `convert_chapter.py`, so an escape that loses a
level -- `\n` where `\\n` was meant -- silently emits a broken f-string, and the *whole page* then
fails at the init cell. This has now happened twice.

`unparsable_cells()` parses every emitted `{marimo}` cell after conversion and prints
`BROKEN CELL at page line N`. It immediately paid for itself by catching a pre-existing one:
Random_numbers had the bare prose `Your code here:` sitting in a code cell, a SyntaxError that
meant the cell never ran. Now commented out in `CONTENT_FIXES`.

## 53. Stray dev servers are what "slow builds" actually were

A build where every page took minutes, and then hung, turned out to be **twelve `myst start`
servers** running at once: 202 marimo processes between them, each server rebuilding on every
file change and competing for CPU. They accumulated because `pkill -f "myst start"` raced with
servers started in backgrounded shells.

Before blaming the content for a slow build, check `ps aux | grep -c "[m]yst"`. With one server
the same tree builds in 46 s.

## 54. Student cells stay flat; only the ones that would raise get wrapped

Wrapping every stub in `def _plot()` was wrong for student cells. It made readers write their own
code inside a function, it looked absurd when the body was mostly commented-out scaffolding, and
it swallowed any `print` the student added at top level.

Stubs are now flat by default: the code sits at cell scope and the last line is
`preview(display=ax, x=x, y=y)`, which supplies the output (and therefore the play button).
`fig`/`ax` become ordinary cell globals, versioned across cells by the usual SSA pass.

But flat everywhere put first-load errors back up from 25 to 64: a live `print("%f" % err)` or
`ax.plot(t, y)` raises while its blank is UNSET. So `needs_display_guard()` wraps *only* the cells
where a live statement actually displays a blank.

**61 of 88 stubs are flat; 27 keep the wrapper. First-load errors stay at 25.**

Most stubs need no guard because the book already comments out the code the student is meant to
write -- the guard is for the minority that hand the student a live `print` or plot.

## Open question for the browser

A `print()` a student adds at top level of a flat cell is *not* captured by `preview()`, which
only wraps the display function. Whether marimo's runtime captures it in an island is unverified:
the island **build** demonstrably does not (see §51), but runtime behaviour may differ. Worth
checking, because students will do this.

## 55. `print` is shadowed so it renders in the cell

Confirmed in a browser: a top-level `print()` in an island goes to the developer console, where
no student will look. `preview()` only wrapped the display function, so it could not catch it.

Rather than teach students a different function, the builtin is shadowed in the page's runtime
cell:

```python
_PRINTED = []

def print(*args, **kwargs):
    buffer = io.StringIO()
    builtins.print(*args, file=buffer, **kwargs)
    _PRINTED.append(buffer.getvalue())

def drain_printed():
    text = "".join(_PRINTED); _PRINTED.clear(); return text
```

`preview()` and `show()` drain the buffer and render it alongside whatever else the cell
displays. Students write ordinary `print(...)` and see ordinary output.

marimo's one-definition rule is satisfied (`print` is bound once, in the runtime cell) and every
cell that prints simply depends on that cell. This also replaced `mo.capture_stdout()` and fixed
the old limitation from §51: a `print` inside a loop that has to stay at top level is now
captured too, because the buffer is global rather than scoped to the display function.

## 56. Printed output shows while the exercise is still unfilled

`preview()` returned the "fill in the code" prompt *before* draining the print buffer, so a
student printing intermediate values as they worked saw nothing until every blank was set --
which is exactly backwards, since printing intermediates is how you get the blanks filled.

It now drains first and stacks both: whatever was printed, then the prompt.

## 57. Only plotting solutions get a display function

`def _plot(): print("..."); show(_plot)` reads absurdly for a solution whose only output is a
print. Now that `print` is buffered globally (§55), such a solution stays flat and simply ends
with `printed()`. The wrapper survives only where it earns its keep -- solutions that plot, where
it keeps `fig`/`ax` out of the global namespace.

## 58. Figures are cell-local (`_fig`, `_ax`), not versioned

The versioning pass was renaming `fig`/`ax` per cell, and the numbers dominated: **141 occurrences
of `ax_3`, `ax_4`, `ax_5`… against 6 plain `fig, ax`**. Underscore-prefixed names are cell-local
in marimo, so every cell can own `_fig, _ax` with no collision and no version suffix.

That also removed the `def _plot()` wrapper from solutions entirely -- its remaining job had been
keeping `fig`/`ax` out of the global namespace, and cell-local names do that for free.

The wrapper survives in one place only: student cells where a live statement would *display* a
blank, where a function is the only way to defer execution until the blank is filled.

Two traps found doing this:

* underscore names must be excluded from the versioning pass in solutions as well as stubs, or
  `_ax` becomes `_ax_sol1` and the `show(_ax)` line that follows cannot see it;
* the `show(...)` line has to be appended **before** renaming, or its keyword names are the
  pre-rename ones -- `show(_plot, dvdt=dvdt)` against a variable that had become `dvdt_2`.

Already-object-oriented cells are now left alone entirely rather than having their `plt.colorbar`
rewritten to `_fig.colorbar`: those cells own their figure under their own names, often inside a
function, and the rewrite invented a name that did not exist there.

## 59. One entry point: `show()`

`preview()`, `printed()` and `show()` became a single `show(*objects, **blanks)` -- a reader
should not have to work out which applies. Every cell ends with it, stub or solution, figure or
print or UI element:

```python
show(x=x, y=y)              # student cell, no figure
show(_ax, npts=npts, x=x)   # student cell that draws
show(_plot, dvdt=dvdt_2)    # deferred: a live statement would display a blank
show(_ax)                   # solution that draws
show()                      # solution whose only output is print
```

It renders, in order: anything printed, any object passed positionally, and -- when there is
nothing else -- a summary of the values the cell defined. `blanks` are keywords so the summary can
name them.

## 60. The init cells are gone: `header:` is a setup cell

The answer bank and the checker used to be two `{marimo}` cells at the top of every page, with
`:editor: false`. They still showed: an empty island each, above the first line of the chapter,
for machinery no reader should ever see.

Both now live in `{marimo-config}`'s `header:`, which the plugin turns into a marimo **setup
cell**. Setup cells are the right tool exactly here:

* `compile_page()` builds them into `notebookCode`, so they execute in the browser like any
  other cell, and
* `outputs_from_stubs(request, request.cells, authored_stubs)` is given only the *authored*
  cells, so a setup cell produces no HTML at all -- not an empty island, nothing.

Verified in the built payload: `runtimeCellCount: 14` against 13 rendered islands, with
`def check_answers` and `ANSWERS = {` present in `notebookCode` and absent from every island.

**The catch, and the correction to note 6.** The earlier finding was "YAML block scalars break
the plugin". That is true only of the one-line option form -- `:pyproject: |` passes the `|`
through as the literal value. The `---`-fenced options block is parsed as real YAML:

````markdown
```{marimo-config}
---
pyproject: dependencies = ["numpy", "matplotlib", "scipy"]
header: |
  import numpy as np
  ...
---
```
````

which is what makes a multi-line header possible at all. Every non-empty line is indented by two
spaces; blank lines stay truly blank.

Since the header is no longer a cell, `unparsable_cells()` cannot see it -- and a broken header
takes the whole page down at load, which is the failure mode that has bitten twice. `main()` now
parses it separately and reports `BROKEN HEADER`.

## 61. `UNSET` is `None`, and unfilledness propagates

Note 46 chose a 2x2 NaN array as the sentinel so that live scaffolding (`x[10]`, `len(x)`,
`h.copy()`) would survive an unfilled blank. It did not survive it usefully: `yt[10]` on a 2x2
raised `IndexError: index 10 is out of bounds for axis 0 with size 2`, which tells a student
nothing, and `is_unanswered` had to guess -- "entirely NaN" cannot distinguish a sentinel from a
result that legitimately came out all-NaN.

`UNSET = None` is honest, and `is_unanswered` collapses to `value is None` plus the object-dtype
case (`np.copy(None)`). The statements that trip over it are guarded explicitly instead.

**The guard.** The run of statements from the first one that would raise, to the end of the cell,
is indented under `if <blank> is not None:`. Contiguous, never reordered -- the old `def _plot()`
wrapper split statements into "safe" and "unsafe" groups, which tore scaffolding comments away
from their code and produced FT1 exercise 10, where `#if ____ > ____:` ended up orphaned inside
the display function at the wrong indentation. The wrapper is now gone from the book entirely.

**Unfilledness travels.** This was the actual FT1 bug, and it was never about the sentinel: cells
14-21 and 25 are not exercises at all, they are the book's own demonstrations, and they failed
because exercise 1 defines `t`, `y` and `fs` and the rest of the chapter is built on them. So the
converter tracks `unset_globals` across the page, and a cell that reads one guards against it
without declaring a placeholder for it (the name belongs to another cell; a rival definition is
what marimo forbids). It travels three ways:

* directly, through a global an earlier stub left unfilled;
* through the hoisted names of a guarded region, which are `None` when the guard does not run;
* through **functions**: PDE2 has the student write `def calc_u(t): return my_idst(uk)`, which
  defines fine and fails two exercises later when called. `unset_fns` maps a function to the
  blanks its body reads, and a caller inherits them.

Three traps, each of which made a guard that could never open or a cell that lost work:

* a name the cell itself binds is not an upstream dependency, even when an earlier exercise used
  the same name -- including it made the guard test a variable the guard assigns;
* a commented hint (`# xsol = ...`) must stay *above* the guard. Left inside it, a student who
  writes their answer where the book tells them to is invisible to the `if` above, and the cell
  waits forever. Only unindented hints move: PDE1's `#delta_max =....` belongs to the loop body
  it sits in;
* only names bound *exclusively* inside the guard get hoisted to `None`. Hoisting one the head
  already set threw away work the cell had legitimately done (`phi = np.zeros([M, M])`).

**Two cases with no value to test.** A stub *function* has no variable to check -- the blank is
its return value -- so `written(f)` tests the body instead: the placeholder `return UNSET`
compiles to a single global lookup, `co_names == ("UNSET",)`, and any real body differs. And a
`while` loop whose exit condition the student has still to write cannot terminate; it gets a
visible `unfinished = True` switch rather than the `mo.stop` it used to have, because `mo.stop`
propagates structurally and took the exercise's own answer check down with the cell (note 45).

Result: 25 failing cells across the book, down to 0.

## 62. Platform assumptions in the content

Linear Algebra exercise 5 asked students to photograph a pen-and-paper derivation, upload the JPG
to "your workspace" with an upload button, and render it with `IPython.display.Image`. There is
no workspace, no upload button and no filesystem here. The derivation is the point of the
exercise and stays; the hand-in mechanics go, via `DROP_CELLS` (the cell) and `PROSE_FIXES` (the
paragraph and the screenshot of the button).

Dropping a cell has to rejoin the prose around it. A markdown block following an exercise closes
it, so the two paragraphs either side of the dropped cell ended exercise 5 after its first
sentence, leaving the Python half of the same exercise outside any exercise at all.

## 63. `given(...)` replaces the condition wall

The guard's condition, spelled out, was the worst thing on the page:

```python
if (
    error_center is not None
    and error_forward is not None
    and yd_analytical is not None
    and yd_center is not None
    and yd_forward is not None
):
```

Five lines of boilerplate above every exercise, burying the one line that matters. It is now
`if given(error_center, error_forward, yd_analytical, yd_center, yd_forward):` -- 90 of the
book's 93 guards fit on one line.

`given` also absorbs `written`, so an exercise asking for a *function* and one asking for a
*value* read identically at the call site; `show()` reports a missing blank with the same
predicate, so the guard and the message can never disagree.

**Not a context manager.** `with given(...):` is the natural shape for "skip this block", but
Python cannot skip a `with` body -- the only way is `sys.settrace` frame hacks, which would be
fragile inside marimo's own instrumented runtime and would break the moment anything else traced
the frame. An `if` with a well-named condition costs one line and no magic.

## 64. The sentinel is written `None`, not `UNSET`

Note 61 made `UNSET` an alias for `None`, which left the pages using both spellings for the same
thing -- `x = UNSET` on one line and `answer_1 = None` three lines below. The alias is gone; the
pages say `None`.

`written()` can no longer test `co_names == ("UNSET",)`, so it compares the function's bytecode
against a reference placeholder instead. Parameter names and arity do not affect `co_code` for a
body of `return None`, so one reference covers every stub in the book.

## 65. Every cell ends in `show(...)`, without exception

54 cells reached the page with no `show(...)` at all, because it was only appended when the cell
had blanks or a figure. Each of those is inert under note 43: no output, no play button, no way
to run it ever.

Now it is unconditional, and `show()` never returns None -- an empty one renders
*"Nothing to display yet."* rather than nothing.

Cells whose own last line was already an expression (`mo.hstack([...])`, `np.sum(answer)`) needed
care: appending `show()` below would have made *it* the last expression and silently swallowed
theirs. `adopt_trailing_display` moves the expression into the call instead. `fig.show()` is the
same case wearing a disguise -- it returns None and draws nothing under islands, so the figure
itself becomes what is displayed.

## 66. Two exercises were answering confidently and wrongly

Worse than an error, because it looks like an answer. Both were unguarded because their blanks
name no variable:

* **ODE1 8.2** (and seven siblings): `def dVdt(t, V): return None` with the integration loop
  commented out. `V = np.empty(N)` then `answer_11_2_1 = np.copy(V)` handed the checker a copy of
  uninitialised memory. A cell that defines a placeholder function is unfinished whether or not
  it calls one, so `stub_fns` now reports every placeholder def, and any `answer_*` computed
  after one is guarded. Only the answer lines -- guarding everything after the def swept up the
  book's own given constants (`x0 = 1`, `h = 0.5`) and left them None.
* **PDE1 10.3**: `#delta[i,j] = ...` inside the relaxation loop. With `delta` left all zeros,
  `delta_max = np.max(np.abs(delta))` is 0, so the loop *exits after one pass* rather than
  hanging, and the initial condition is returned as the answer. There is nothing here to declare
  as None and nothing to test, so it gets the same visible `_unfinished` switch as a loop that
  cannot terminate. Three cells in the book need it, all in PDE1.

The switch is underscore-prefixed: it is per-cell state, and marimo makes underscore names
cell-local, which is also what stops three of them colliding on one page.

## 67. Session setup is hoisted, not hidden

`plt.rcParams['figure.dpi'] = 100` opened every chapter in its own visible cell. It is
configuration, not content, and there is nothing in it for a reader to change, so
`collect_setup()` folds it into the page header beside the imports. Eleven fewer cells.

## 68. Two exercises were answering with uninitialised memory

Note 66 caught the first pair of these; running every check cell on a *fresh* page found the rest.
The test is precise: a check that returns green or red before the reader has typed anything is a
bug, and only amber ("waiting") is correct.

* **RF 3.3**: the book pre-allocates `sol6 = np.zeros(polyorder)` for the student to fill element
  by element. That assignment defeated the `sol6 = None` placeholder, so `given(sol6)` was true
  on load and the checker marked an array of zeros wrong before the reader had done anything.
* **ODE2 9.8**: `tf1 = np.empty(Ni)` and two loops whose bodies are `...`.

`self_assigned()` now finds candidate blanks the cell assigns for itself and drops them: they can
gate nothing. The same rule fixes the opposite failure, where `t1 = find_tf(v1)` is assigned
*inside* the guard and `given(t1)` could therefore never become true -- the cell was dead however
much the reader filled in.

When dropping them leaves nothing testable, `unfinished_line()` falls back to the `_unfinished`
switch, extended to recognise a loop whose body the student has still to write.

## 69. 65 KB of output was one progress line

PDE1's relaxation solutions print `"N_iter %d delta_max %e\r" % (...)` once per iteration with
`end=""`. In a terminal each write overwrites the last and the reader watches one line count up.
Concatenated into the print buffer it became **65,778 characters in three newlines and 1909
carriage returns** -- a single unreadable line, and the worst output in the book.

`drain_printed` now applies carriage returns the way a terminal would, keeping the last non-empty
write of each line. 65,778 characters become 104, and the final iteration count survives:

```
N_iter 1909 delta_max 9.995942e-05
Total running time: 0.12 min
Code speed: 258.9 iterations per second
```

Across the whole book this took the built payload from **10.2 MB to 4.3 MB** -- the progress text
was being baked into the build-time output of every one of those cells.

`format_printed` is the backstop for output that is genuinely long: more than 16 lines shows the
first 12 and last 4, with the rest behind an `mo.accordion`.

## 70. Solutions that showed nothing now show what they computed

Five solutions neither plotted nor printed, so the reader opened the dropdown to a cell that
displayed nothing -- and executable solutions were chosen *because* their output is the teaching.
`answer_sources()` reads the variables behind each `answer_* = ...` line and hands them to
`show()`, so NI 2.2 now renders "`trapezoidal_integral` = 0.333" and FT1 5.1 the shapes of `t`
and `y`. The `answer_*` key itself is bookkeeping and is never what the reader wants to see.

## 71. Distinguishing a blank from commented-out code

`STUB_HINT_RE` only stripped `# name = ` with a dotted or empty right-hand side, so 18 solutions
still carried the blanks they were the answer to. Widening the regex naively would have deleted
the author's own commented alternatives (`#x=a+(b-a)*np.random.rand(N)`), which are content.

`is_stub_hint()` replaces it with a predicate: a blank always *shows its gap* -- an empty
right-hand side, or a run of dots or underscores standing in for what the reader must supply --
and the gap can be in the subscript rather than the value (`# rho_fixed[___,___] = 1`,
`# V[0] = ____`, `# T[...] = 20`).

## 72. Hand edits: what the converter could not decide

The converter is frozen as of this point; the rest is edited directly in the markdown.

* **Animations (PDE2, 4 cells).** `FuncAnimation` + `jshtml` is awkward in a reactive page and
  unverified under islands. Replaced with `mo.ui.slider` over the time index: the plot redraws
  itself as the slider moves, which is the same reactive model the rest of the book now uses.
  Doing this exposed a real break: `calc_u` is tied to exercise 3's `uk0`, and marimo gives each
  cell its own, so the "fun initial condition" at the end of the chapter never actually reached
  the plot. It now has its own `calc_u_2`.
* **FT2 6.5 was not an exercise.** Its prose introduces the mask that exercise 6.6 builds, and
  the cell between them is a `meshgrid` demonstration. The wrapper is gone and the demo is
  read-only. FT2 has 7 exercises now, not 8.
* **FT2 sliders** were defined in one cell and read in another (marimo requires this for
  reactivity), which in the solution dropdown put them above a screen of code, far from the image
  they control. The image cell now displays them itself -- `show()` already vstacks several
  positional arguments -- and the defining cell says where they went.
* **Six dropdown solutions sat outside any exercise**, because the source wrote `**Solution:**`
  with no preceding `**Exercise N**`. They are real exercises and are now `{exercise-start}` /
  `{solution-start}` pairs (`ex_6_03b`, `ex_6_05b`, `ex_6_06b`, `ex_9_03b`, `ex_9_03c`,
  `ex_11_09b`). **This renumbers exercises after each insertion point.**

Deliberately left alone: three stubs (FT2 6.2/6.7, ODE1 8.7) comment out the *entire* plot
including the figure, because the exercise is to write it. That is a different design from the 37
stubs that supply the axes, not an inconsistency with them.

## 73. Editor height: blocked by the shadow DOM

A quarter of the book's cells run over 30 lines and the longest is 64, which pushes their own
output off the screen. `static/custom.css` (wired up via `site.options.style`) caps `.cm-editor`
at 28rem and lets `.cm-scroller` scroll.

**Unverified, and probably ineffective**: the islands bridge mounts each cell behind a shadow root
(`.marimo-island-host`, and the bridge walks `shadowHostsIn(host)`), and ordinary page CSS does
not cross a shadow boundary. If it has no effect the height has to come from inside marimo
instead. The file is harmless either way.

## 74. The header may not define a single underscore name

Every cell on every page died with:

```
Name `_last_write` is not defined. Names prefixed with an underscore are local to the cell
that defines them. `_last_write` is defined as a cell-local name in cell-0
```

The header compiles to one marimo **setup cell**, and marimo makes an underscore-prefixed name
local to the cell that defines it (note 61, and the About page teaches it). Everything the header
defines -- `show`, `given`, `check_answers`, the print buffer -- is shared machinery called from
every other cell, so a leading underscore is exactly wrong there. Three names had one: `_PRINTED`,
`_last_write`, `_unwritten`.

**What let it through is that it does not fail consistently.** `_PRINTED` was read directly inside
a function body and resolved fine; `last_write` was called from inside a *generator expression*

```python
return "\n".join(last_write(line) for line in text.split("\n"))
```

and a comprehension is a nested scope that marimo's cell-local rewriting does not reach. So the
same mistake was already in the header, working, before the one that broke the book.

Neither guard caught it. `validate_page.py` runs the header with plain `exec`, which has no
concept of cell-local names, and the build succeeded because the error is at *hydration*, not at
compile time -- the static artefact says nothing about what the hydrated app does (note 12).

Both now check it structurally: `header_locals()` in the converter (`HEADER DEFINES A CELL-LOCAL`)
and the same test in `validate_page.py`, which returns non-zero.

## 75. Solutions need their own picture, not the reader's

PDE2's three solutions computed the answer and printed a timing line, and that was all a reader
saw on opening the dropdown. The interactive slider that steps through the result sits *outside*
the solution and is guarded on the **student's** variables, so someone who opens the solution
without having done the exercise sees "Waiting for `t`, `x`" there and never sees the physics.

Each solution now draws its own snapshots across time from its `_sol` variables -- diffusion
smoothing out, FTCS diverging on the wave equation, the spectral method staying bounded. A
reference answer wants a picture of the result at a glance, which is a different job from the
slider's, so this is not a duplicate of it.

A slider in the solution would have cost two more cells each (marimo needs a UI element defined
in one cell and read in another), for a worse view of the same data.

## 76. Editor height: confirmed unreachable from page CSS

Measured in the browser rather than guessed at:

```js
document.querySelectorAll('.cm-editor').length          // 0
[...document.querySelectorAll('*')].filter(e => e.shadowRoot).length   // 58
```

Zero editors in the document, 58 open shadow roots. The bridge is not the barrier -- it empties
the anywidget's shadow root and fills it with a `<slot>` (slotted content stays in the light DOM),
and `installMarimoIslandStyles` appends marimo's stylesheet to the *top-level* `document.head`.
The shadow roots are marimo's own, created by the islands runtime around each cell's UI, with
their own adopted stylesheet. `.marimo-island-host .cm-editor` can never match.

**The fix is to cap the shadow host.** A shadow host is an ordinary light-DOM element and its box
is styleable from outside even though its contents are not. Devtools named it:

```js
[...document.querySelectorAll('*')]
  .filter(e => e.shadowRoot?.querySelector('.cm-editor'))
  .map(e => e.tagName)        // ['MARIMO-CODE-EDITOR', ...]
```

so `static/custom.css` is now:

```css
marimo-code-editor { display: block; max-height: 28rem; overflow: auto; }
```

`display: block` is the part that matters and the reason a first attempt at this would fail
anyway: a custom element is `display: inline` by default, and `max-height` does nothing on an
inline box.

The alternative -- injecting a `<style>` into each open shadow root with JS -- has nowhere to
live: the book-theme exposes no script hook (`site.options` is `style`, a CSS file, plus booleans
and strings), so it would mean patching the installed plugin, which would not survive a deploy.

**Watch for**: scrolling now happens on the host, not on CodeMirror's own `.cm-scroller`, so the
view may not follow the cursor when typing past the bottom of a capped cell. If it does not,
the cap has to come from inside marimo instead.

## 77. Data files, and why the repository is public

The two datasets the book loads -- `data.dat` (5 MB, FT1 exercise 6) and `velocities.dat` (NI
exercise 6) -- live in `data/` and are fetched at runtime from this repository's `main` branch.
There is no filesystem in the browser, so they have to come over the network; `load_data` falls
back to the local copy under `data/` at build time.

This is the one thing that forces the repository's visibility: **raw.githubusercontent.com does
not serve a private repository without a token**, and there is nowhere to put a token in a page
that 200 students load. The sibling `lecture-tn2626-statistical-physics` is private, so this is a
deliberate difference, taken so the book depends on nothing outside itself -- the alternative was
to keep fetching from the original TUDelft-books repository, which works today only because that
repository happens to be public and stay that way.

Verified after pushing, against the URL actually baked into the pages:

```
data.dat        HTTP 200, 5049921 bytes
velocities.dat  HTTP 200,    1241 bytes
access-control-allow-origin: *
```

That last header matters as much as the 200: Pyodide's `open_url` is a cross-origin request from
the site to raw.githubusercontent, and would fail silently without it.

**Renaming the repository, moving it to an organisation, or making it private all break the
book.** `DATA_URL` is baked into every chapter's `{marimo-config}` header.

## 78. What is under version control

`scripts/` and `README.md` are committed but excluded from the book build (`myst.yml: exclude`).
`.jupyter-book-marimo/` is not committed: it is a byte-identical copy of the plugin's shipped
assets, written at build time.

The chapters are generated files that are now edited by hand, so **the converter is frozen** --
re-running it would discard every hand edit recorded in note 72 and after. It stays in the tree
because these notes are only legible next to the code they describe.

## 79. Why there is no CI

The Curvenote reusable workflows failed on the first push:

```
⛔️ .venv/bin/jupyter-book-marimo Unknown plugin, it must be an executable file
Error: ENOENT: no such file or directory, stat '.venv/bin/jupyter-book-marimo'
```

`curvenote/actions/.github/workflows/submit.yml@v1` runs inside `ghcr.io/curvenote/cli:latest`
and its steps are checkout → (optional fonts) → `curvenote check` / `curvenote submit`. There is
no input and no step between checkout and the CLI where project dependencies could be installed,
and this book cannot build without them: the plugin is an executable resolved from `.venv/bin/`,
and it executes every code cell at build time, so numpy, matplotlib, scipy and marimo all have to
be there.

Both workflows are removed; deployment is `curvenote submit curious-beams --kind article
--collection articles` run by hand, where the venv already exists.

**It is fixable if automatic submission is ever wanted.** `curvenote/actions/submit@main` is a
*composite* action -- it only runs `curvenote submit` and assumes the CLI is on PATH -- so a
hand-written job can install first:

```yaml
runs-on: ubuntu-latest
steps:
  - uses: actions/checkout@v4
  - uses: astral-sh/setup-uv@v6
  - run: uv sync --frozen
  - run: npm install -g curvenote
  - uses: curvenote/actions/submit@main
    with: {venue: curious-beams, kind: article, collection: articles, id: ..., working-directory: .}
```

Running on a plain `ubuntu-latest` rather than their container keeps it standard; the cost is
losing the Typst and image tooling their image carries, which this project (exporting `meca`)
does not use. Expect several minutes a run -- the marimo plugin executes every cell in the book.
