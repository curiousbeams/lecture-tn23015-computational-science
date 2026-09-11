"""Rewrite pyplot state-machine plotting into the object-oriented ``fig, ax`` idiom.

Two reasons, one pedagogical and one mechanical:

* it is the style the course teaches -- ``fig, ax = plt.subplots()``, ``ax.plot(...)``, end on
  ``ax``;
* marimo displays a cell's *last expression*, while matplotlib's figure registry is global
  across cells. Implicit "current figure" code made every solution display a figure, usually the
  previous cell's. An explicit figure per cell removes the ambiguity at the source instead of
  papering over it with ``plt.close("all")``.

The source book's plotting vocabulary is small and regular: ``plot``/``xlabel``/``ylabel`` are
about 60% of ~700 calls, every multi-panel call uses the compact single-row form
(``plt.subplot(121)``), and only two cells in the whole book plot inside a function body. Those
two are reported rather than guessed at.
"""

from __future__ import annotations

import ast
import re

# plt.foo(...) -> ax.foo(...)
AXES_SAME = {
    "plot", "scatter", "imshow", "hist", "hist2d", "bar", "barh", "step", "stem",
    "errorbar", "fill_between", "fill", "loglog", "semilogx", "semilogy", "contour",
    "contourf", "pcolormesh", "pcolor", "axhline", "axvline", "axhspan", "axvspan",
    "text", "annotate", "legend", "grid", "arrow", "quiver", "streamplot", "matshow",
    "boxplot", "violinplot", "hlines", "vlines", "axis", "set_aspect", "minorticks_on",
}

# plt.foo(...) -> ax.set_foo(...)
AXES_SET = {
    "xlabel": "set_xlabel", "ylabel": "set_ylabel", "title": "set_title",
    "xlim": "set_xlim", "ylim": "set_ylim", "xscale": "set_xscale",
    "yscale": "set_yscale", "xticks": "set_xticks", "yticks": "set_yticks",
}

# plt.foo(...) -> fig.foo(...)
FIG_SAME = {"colorbar", "tight_layout", "savefig", "suptitle"}

# dropped entirely: marimo renders the cell's last expression
DROP = {"show"}

# calls whose return value a bare plt.colorbar() would have used
MAPPABLE = ("imshow", "pcolormesh", "pcolor", "scatter", "contourf", "matshow", "hist2d")

PLOTTING = AXES_SAME | set(AXES_SET) | {"subplots", "subplot", "figure"}

SUBPLOT_LINE = re.compile(r"^(\s*)plt\.subplot\(\s*(\d{3})\s*\)\s*$")
FIGURE_LINE = re.compile(r"^(\s*)plt\.(subplots|figure)\((.*)\)\s*$")
BARE_COLORBAR = re.compile(r"plt\.colorbar\(\s*\)")


def _calls(node: ast.AST) -> set[str]:
    return {
        n.attr
        for n in ast.walk(node)
        if isinstance(n, ast.Attribute)
        and isinstance(n.value, ast.Name)
        and n.value.id == "plt"
    }


def to_object_oriented(
    source: str, blanks: tuple[str, ...] = (), *, wrap: bool = True
) -> tuple[str, list[str], str | None]:
    """Return ``(converted_source, notes)``. Notes flag anything left for a human.

    ``blanks`` are the names a student still has to fill in. Statements that *display* something
    from a blank -- a plot, a print -- are moved into the guarded display function so an unfilled
    stub renders a prompt instead of raising. Assignments are deliberately left outside it, so
    the cell always runs to completion and always defines its ``answer_*`` variables.
    """
    if "plt." not in source and not blanks and "print(" not in source:
        return source, [], None
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, ["unparsable, left in pyplot style"], None
    if "plt." not in source:
        # no plotting, but blanks and prints still need the display function
        return (*_wrap_plotting(source, None, [], blanks, wrap=wrap), None)

    # Already object-oriented -- someone assigned the result of plt.subplots. Don't restructure,
    # but still rewrite the stray `plt.xlabel(...)` calls these cells mix in (the PDE2 animation
    # cells do exactly that), so the whole book ends up in one idiom.
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            fn = node.value.func
            if isinstance(fn, ast.Attribute) and fn.attr == "subplots":
                # `fix, ax = plt.subplots(...)` is a typo in the source book
                fixed = re.sub(r"\bfix(\s*,\s*ax\b)", r"fig\1", source)
                note = ["typo `fix` -> `fig` corrected"] if fixed != source else []
                # Deliberately *not* renamed: these cells already own their figure under their
                # own names (`fig, axes = plt.subplots(...)`, often inside a function). Mapping
                # `plt.colorbar` to `_fig.colorbar` invented a name that does not exist there.
                return fixed, note, None

    defs = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    top_plots = any(_calls(s) & PLOTTING for s in tree.body if not isinstance(s, defs))
    fn_plots = any(_calls(s) & PLOTTING for s in tree.body if isinstance(s, defs))
    if fn_plots and not top_plots:
        return source, ["plots inside a function body -- convert by hand"], None
    if not top_plots:
        # only plt.rcParams and friends
        return (*_wrap_plotting(_rename_calls(source), None, [], blanks, wrap=wrap), None)

    lines = source.split("\n")

    # --- multi-panel layout, always the compact single-row form in this book ---
    panels = [
        (i, int(m.group(2)))
        for i, line in enumerate(lines)
        if (m := SUBPLOT_LINE.match(line))
    ]
    nrows = ncols = 1
    if panels:
        code = panels[0][1]
        nrows, ncols = code // 100, (code // 10) % 10

    # --- find (or invent) the figure-creating line ---
    fig_idx = next((i for i, line in enumerate(lines) if FIGURE_LINE.match(line)), None)
    layout = f"{nrows}, {ncols}, " if panels else ""
    # underscore-prefixed: marimo treats these as cell-local, so every cell can have its own
    # `_fig, _ax` and the versioning pass never touches them. Without this the book was full of
    # `ax_3`, `ax_4`, `ax_5` -- 141 of them against 6 plain `fig, ax`.
    axes_name = "_axs" if panels else "_ax"

    if fig_idx is not None:
        m = FIGURE_LINE.match(lines[fig_idx])
        indent, args = m.group(1), m.group(3).strip()
        # plt.figure(figsize=...) and plt.subplots(figsize=...) both become plt.subplots(...)
        args = re.sub(r"^\d+\s*,\s*\d+\s*,?\s*", "", args)
        joined = layout + args if args else layout.rstrip(", ")
        lines[fig_idx] = f"{indent}_fig, {axes_name} = plt.subplots({joined.rstrip(', ')})"
    else:
        first = next(
            (
                s.lineno - 1
                for s in tree.body
                if not isinstance(s, defs) and _calls(s) & PLOTTING
            ),
            0,
        )
        indent = re.match(r"\s*", lines[first]).group(0)
        lines.insert(first, f"{indent}_fig, {axes_name} = plt.subplots({layout.rstrip(', ')})")
        panels = [(i + 1 if i >= first else i, c) for i, c in panels]

    # --- each plt.subplot(1NK) becomes a hop to the next axes ---
    for idx, code in panels:
        indent = SUBPLOT_LINE.match(lines[idx]).group(1)
        k = code % 10
        lines[idx] = f"{indent}_ax = _axs[{k - 1}]"

    # --- a bare plt.colorbar() needs the mappable it used to grab implicitly ---
    notes: list[str] = []
    if BARE_COLORBAR.search("\n".join(lines)):
        # Each bare plt.colorbar() belongs to the mappable most recently drawn, not to the
        # first one in the cell. Reusing a single `_im` put all three colorbars of the
        # three-panel derivative figure on the left-hand axis, because `fig.colorbar(mappable)`
        # steals space from that mappable's own axes.
        mappable_re = re.compile(rf"^(\s*)plt\.({'|'.join(MAPPABLE)})\(")
        count = 0
        current: str | None = None
        rebuilt: list[str] = []
        for line in lines:
            m = mappable_re.match(line)
            if m:
                count += 1
                current = f"_im{count}"
                rebuilt.append(f"{m.group(1)}{current} = " + line.lstrip())
                continue
            if re.search(r"\bplt\.clim\s*\(", line):
                # clim acts on the "current image", i.e. the one most recently drawn
                if current is None:
                    notes.append("plt.clim() with no preceding mappable -- check by hand")
                    rebuilt.append(line)
                else:
                    rebuilt.append(re.sub(r"\bplt\.clim\s*\(", f"{current}.set_clim(", line))
                continue
            if BARE_COLORBAR.search(line):
                if current is None:
                    notes.append("bare plt.colorbar() with no preceding mappable -- check by hand")
                    rebuilt.append(line)
                else:
                    rebuilt.append(BARE_COLORBAR.sub(f"_fig.colorbar({current})", line))
                continue
            rebuilt.append(line)
        lines = rebuilt


    lines = [ln for ln in lines if ln.strip() not in {f"plt.{d}()" for d in DROP}]
    out = _rename_calls("\n".join(lines))

    tail = "_fig" if panels else "_ax"
    body, more = _wrap_plotting(out, tail, notes, blanks, wrap=wrap)
    return body, more, (tail if not wrap else None)


PLOT_NAMES = {"plt", "_ax", "_axs", "_fig"}
IM_NAME = re.compile(r"^_im\d*$")


RCPARAMS = re.compile(r"^\s*plt\.rcParams\b")


def _is_config(chunk: str) -> bool:
    """`plt.rcParams[...] = ...` is configuration, not something to display."""
    return all(
        RCPARAMS.match(line) or not line.strip() or line.strip().startswith("#")
        for line in chunk.split("\n")
    )


def _is_plot_name(name: str) -> bool:
    # `_im1.set_clim(...)` is plotting state; without matching the numbered mappables it was
    # hoisted out of _plot() and ran before the mappable existed
    return name in PLOT_NAMES or bool(IM_NAME.match(name))


def _wrap_plotting(
    source: str,
    tail: str | None,
    notes: list[str],
    blanks: tuple[str, ...] = (),
    *,
    wrap: bool = True,
) -> tuple[str, list[str]]:
    """Move the plotting statements into a cell-local function that returns the axes.

    Every plotting cell would otherwise bind the globals `fig` and `ax`, and marimo allows a
    global to be defined by only one cell -- with ~76 plotting cells in the book that is 76
    collisions. Wrapping is also what marimo's own documentation recommends for exactly these
    names ("the variables plt, fig, and ax aren't added to the globals").

    Only the plotting statements move. Data assignments stay at the top level, because later
    exercises and later solutions genuinely read them; that chain is the thing an earlier
    attempt at wrapping broke. `_plot` is underscore-prefixed, so it is cell-local too.
    """
    if not wrap:
        # student cells stay flat: the caller appends `preview(display=ax, ...)`
        return source, notes
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, [*notes, "unparsable after conversion -- left inline"]

    # Split by *line ranges*, not ast.get_source_segment: the segment of a statement excludes
    # the comments around it, and this book's scaffolding is largely comments
    # ("# x = ....", "# Now the plot"). Losing them would gut the exercises.
    lines = source.split("\n")
    head: list[str] = []
    body: list[str] = []
    cursor = 0
    for stmt in tree.body:
        end = (stmt.end_lineno or stmt.lineno)
        chunk = "\n".join(lines[cursor:end])
        cursor = end
        names = {
            n.id for n in ast.walk(stmt) if isinstance(n, ast.Name)
        } | {
            n.value.id
            for n in ast.walk(stmt)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
        }
        is_plot = any(_is_plot_name(n) for n in names)
        is_print = (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name)
            and stmt.value.func.id == "print"
        )
        # A statement that *shows* something built from a blank must be guarded too, or an
        # unfilled stub raises on `print("%f" % UNSET)`. Assignments stay outside the guard so
        # the cell still defines its answer_* variables and the check below it can run.
        shows_blank = bool(names & set(blanks)) and not isinstance(
            stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.FunctionDef, ast.ClassDef)
        )
        if is_plot and _is_config(chunk):
            head.append(chunk)
            continue
        (body if is_plot or shows_blank or is_print else head).append(chunk)
    trailing = "\n".join(lines[cursor:]).rstrip()
    if trailing:
        head.append(trailing)

    indented = "\n".join(
        "\n".join(f"    {ln}" if ln.strip() else "" for ln in chunk.split("\n"))
        for chunk in body
    )
    has_body = bool([c for c in body if c.strip()])
    if not has_body and not blanks:
        return source, notes

    if not has_body:
        return "\n".join(head).strip("\n"), notes

    indented = "\n".join(
        "\n".join(f"    {ln}" if ln.strip() else "" for ln in chunk.split("\n"))
        for chunk in body
    )
    # the caller appends the `show(_plot, ...)` line
    closing = [f"    return {tail}"] if tail else []
    parts = [*head, "", "def _plot():", indented, *closing]
    return "\n".join(p for p in parts if p is not None).strip("\n"), notes


INLINE_CODE = re.compile(r"`([^`\n]+)`")
PROSE_SUBPLOT = re.compile(r"\b(?:plt|fig)\.subplot\(\s*(\d{3})\s*\)")
PROSE_SUBPLOTS = re.compile(r"\b(?:plt|fig)\.subplots\(")


def convert_prose(text: str) -> str:
    """Apply the same rewrite to inline code spans in the prose.

    The chapters tell students which commands to type -- "run the command `plt.subplot(121)`" --
    so leaving the prose alone would have it contradict the converted code and the solutions.
    Only backticked spans are touched, so ordinary words are safe.
    """

    def fix(match: re.Match) -> str:
        span = match.group(1)
        if "plt." not in span and "fig.subplots" not in span:
            return match.group(0)
        span = PROSE_SUBPLOT.sub(lambda m: f"ax = axs[{int(m.group(1)) % 10 - 1}]", span)
        span = PROSE_SUBPLOTS.sub("fig, ax = plt.subplots(", span)
        span = _rename_calls(span)
        return f"`{span}`"

    return INLINE_CODE.sub(fix, text)


def _rename_calls(source: str) -> str:
    """Rewrite the plt.* call prefixes, leaving arguments and formatting untouched."""
    for name in sorted(AXES_SAME, key=len, reverse=True):
        source = re.sub(rf"\bplt\.{name}\s*\(", f"_ax.{name}(", source)
    for name, new in sorted(AXES_SET.items(), key=lambda kv: -len(kv[0])):
        source = re.sub(rf"\bplt\.{name}\s*\(", f"_ax.{new}(", source)
    for name in sorted(FIG_SAME, key=len, reverse=True):
        source = re.sub(rf"\bplt\.{name}\s*\(", f"_fig.{name}(", source)
    source = re.sub(r"\bplt\.gca\(\s*\)", "_ax", source)
    source = re.sub(r"\bplt\.gcf\(\s*\)", "_fig", source)
    return source
