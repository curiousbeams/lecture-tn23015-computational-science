"""The in-page runtime: everything a chapter's cells call that is not numpy or marimo.

This is the single source of truth. It is *copied* into each chapter's `{marimo-config}` header
by `sync_checker.py` rather than imported, because there is no import to make: the header becomes
a marimo setup cell running in the browser, where there is no filesystem and no package to
install. MyST substitutions do not reach directive options (tested: `{{ checker }}` is passed
through literally and the compile fails), and the plugin offers no include mechanism.

Copying keeps each page self-contained -- no extra network fetch to fail on load -- at the cost
of ~280 duplicated lines per chapter, which nobody reads. Editing this file and running

    .venv/bin/python scripts/sync_checker.py

is what keeps the eleven copies honest; the script refuses to run if they have drifted apart.

`ANSWERS` is *not* here: the answer bank is per chapter, and the converter writes it above this
block.
"""

def reference_answer(key):
    """Return (expected, comparator) for a stored answer, handling downsampled entries."""
    raw = ANSWERS[key]
    if isinstance(raw, dict) and raw.get("__downsampled__"):
        stride = raw["stride"]
        shape = tuple(raw["shape"])
        vals = raw["values"]
        sol = to_array(vals)
        return sol, shape, stride
    sol = to_array(raw)
    return sol, sol.shape, 1


def to_array(v):
    if isinstance(v, dict) and "real" in v:
        return np.array(v["real"]) + 1j * np.array(v["imag"])
    return np.array(v)


def diff_report(sol, ans, atol):
    lines, n = [], 0
    sol, ans = np.atleast_1d(sol), np.atleast_1d(ans)
    for idx in np.ndindex(sol.shape):
        if not np.isclose(sol[idx], ans[idx], atol=atol):
            lines.append(f"  {idx}  expected {sol[idx]:.6g}   yours {ans[idx]:.6g}")
            n += 1
            if n >= 10:
                lines.append("  ... (only the first 10 shown)")
                break
    return "\n".join(lines)


def describe(value):
    """One-line description of a value the student has produced."""
    arr = np.asarray(value)
    if arr.dtype == object:
        return "set"
    if arr.ndim == 0:
        return f"= {arr.item():.6g}" if np.issubdtype(arr.dtype, np.number) else "set"
    return f"shape {arr.shape}"


# There is no filesystem in the browser, so the two data files the book uses are fetched over
# the network. They are served from this repository's own `data/` directory rather than from the
# original book's, so the port depends on nothing outside itself -- which is why the repository
# is public: raw.githubusercontent.com does not serve a private repo without a token.
DATA_URL = (
    "https://raw.githubusercontent.com/curiousbeams/"
    "lecture-tn23015-computational-science/main/data/"
)


def load_data(name, **kwargs):
    """np.loadtxt for a data file, working both in the browser and at build time."""
    try:
        from pyodide.http import open_url  # only exists under Pyodide
    except ImportError:
        return np.loadtxt("data/" + name, **kwargs)  # build time: the local copy
    return np.loadtxt(open_url(DATA_URL + name), **kwargs)


PRINTED = []


def print(*args, **kwargs):
    """`print` that shows up in the cell, not the browser console.

    marimo's islands do not surface stdout: a top-level `print` in a student's cell went to the
    developer console, where no student will look. Rather than teach a different function, the
    builtin is shadowed to buffer its output; `preview()` and `show()` drain the buffer and
    render it with whatever else the cell displays.
    """
    import builtins
    import io

    kwargs.pop("file", None)
    buffer = io.StringIO()
    builtins.print(*args, file=buffer, **kwargs)
    PRINTED.append(buffer.getvalue())


def drain_printed():
    """Everything the cell printed, with carriage returns applied as a terminal would.

    `print("N_iter %d\r" % n, end="")` is a progress line: in a terminal each update overwrites
    the last, and the reader sees one line counting up. Concatenated into a buffer instead, PDE1's
    relaxation solution produced 65 KB of text in three newlines and 1909 carriage returns -- one
    unreadable line, and the single worst piece of output in the book. Keeping only what follows
    the last `\r` of each line is what the author wrote the `\r` to mean.
    """
    text = "".join(PRINTED)
    PRINTED.clear()
    return "\n".join(last_write(line) for line in text.split("\n"))


def last_write(line):
    # The final segment is usually empty -- the progress line ends with a carriage return and the
    # summary that follows begins with a newline -- so it is the last *non-empty* write that the
    # reader would have been left looking at.
    written = [seg for seg in line.split("\r") if seg]
    return written[-1] if written else ""


# Long output is folded away rather than dumped: a solution that prints a row per iteration
# should not push the next exercise off the screen.
PRINT_HEAD, PRINT_TAIL = 12, 4


def format_printed(text):
    text = text.rstrip()
    lines = text.split("\n")
    if len(lines) <= PRINT_HEAD + PRINT_TAIL + 1:
        return mo.md(f"```text\n{text}\n```")
    hidden = len(lines) - PRINT_HEAD - PRINT_TAIL
    shown = [*lines[:PRINT_HEAD], f"... {hidden} more lines ...", *lines[-PRINT_TAIL:]]
    return mo.vstack([
        mo.md("```text\n" + "\n".join(shown) + "\n```"),
        mo.accordion({f"Show all {len(lines)} lines": mo.md(f"```text\n{text}\n```")}),
    ])


def unwritten_stub(_x):
    return None


def written(fn):
    """True once a placeholder function has been given a real body.

    Some exercises ask for a function rather than a value: the stub is `def f(x): return None`,
    so `f(x)` gives None and whatever is built from it -- a plot, an index, a mean -- fails.
    There is no variable to test here, because the blank *is* the return value and that only
    exists once the function is called. So the body is what gets tested, by comparing its
    bytecode against the placeholder above. Parameter names and count do not affect it; any
    real body does.
    """
    code = getattr(fn, "__code__", None)
    return code is None or code.co_code != unwritten_stub.__code__.co_code


def given(*values):
    """True once every blank a cell is waiting on has been filled in.

    This is the whole condition of the guard that fronts an unfinished exercise. Spelled out it
    was a wall -- `if a is not None and b is not None and c is not None and ...`, five deep and
    wrapped over six lines, burying the one thing the reader needs to see.

    A function argument is tested with `written`, so an exercise that asks for a function and one
    that asks for a value read the same way at the call site. Everything else goes through
    `is_unanswered`, the same test the checker uses -- "not None" is not enough, because an
    answer built from an unfilled blank is `np.copy(None)`, a 0-d object array that is perfectly
    not-None and would open a guard downstream of it.

    (A context manager would be the natural shape for "skip this block", but Python has no way to
    skip a `with` body without frame-tracing tricks, and those would be fragile inside marimo's
    own instrumented runtime. An `if` with a well-named condition costs one line and no magic.)
    """
    return all(written(v) if callable(v) else not is_unanswered(v) for v in values)


def show(*objects, **blanks):
    """The last line of every cell -- stub or solution, figure, print or UI element.

    One entry point rather than three (`preview`, `printed`, `show`), because a reader should not
    have to work out which applies. It renders, in order:

    * anything the cell printed (see `print` above);
    * any figure, axes or UI element passed positionally;
    * a summary of the values the cell defined, when there is nothing else to show.

    A marimo island with no output has no play button -- and with no play button the cell can
    never be run, so a cell that displays nothing is inert. That is why this is never optional.

    `blanks` are passed by keyword so the prompt can name them. While any is still None the cell
    is unfinished, and says which name it is waiting for -- it may well belong to an earlier
    exercise, in which case there is nothing to fill in *here* and a generic "fill this in"
    would send the reader looking in the wrong place. Anything already printed is shown
    regardless, since printing intermediate values is how a student works towards an answer.
    """
    displays = list(objects)
    missing = [k for k, v in blanks.items() if not given(v)]

    text = drain_printed()
    blocks = []
    if text.strip():
        blocks.append(format_printed(text))
    blocks.extend(d for d in displays if d is not None)

    if missing:
        names = ", ".join(f"`{m}`" for m in missing)
        blocks.append(mo.md(f"*Waiting for {names}.*"))
    elif not blocks and blanks:
        blocks.append(
            mo.md(" · ".join(f"`{k}` {describe(v)}" for k, v in blanks.items()))
        )
    if not blocks:
        # Never None. A cell whose output is None has no play button, so it cannot be run --
        # not now, and not after the reader fills it in either.
        blocks.append(mo.md("*Nothing to display yet.*"))
    return blocks[0] if len(blocks) == 1 else mo.vstack(blocks)


def is_unanswered(value):
    """True while an answer is still built out of unfilled placeholders.

    Identity alone is not enough: `answer_3_02_1 = (yd_forward, error_forward)` is a *tuple* of
    sentinels, and `answer_7_06_1 = np.copy(y)` on an unfilled `y` is a 0-d object array. Both
    have to read as unanswered, or the checker marks work wrong before it has been attempted.

    With `None` as the sentinel this is decidable. Under the old 2x2-NaN one it was not: the test
    had to be "entirely NaN", which cannot tell a sentinel from a real result that legitimately
    came out all-NaN.
    """
    if value is None:
        return True
    if isinstance(value, (tuple, list)):
        return any(is_unanswered(v) for v in value)
    arr = np.asarray(value)
    return arr.dtype == object


def check_answers(*values, key, start=1, when=True, **named):
    """Compare the student's answers against the stored reference values.

    Answers are handed over under the names the student gave them:

        check_answers(x=x, y=y, y_prime=y_prime, key="answer_3_01")

    so a wrong answer can be reported as `y_prime` rather than as `answer_3_01_3` -- a name that,
    since the `answer_*` variables were folded into this call, exists nowhere in the exercise.
    `key` plus the position in the call still selects the stored value to compare against, and
    `start` is the index of the first one, for the few exercises that were split in two and whose
    second half owns `..._4` onwards rather than `..._1`.

    `when` gates the check. Some exercises hand out a pre-allocated `np.empty(N)` for the student
    to fill: perfectly not-None, and so graded as wrong before a line has been written. Those pass
    the condition that says the work has started -- `when=given(dVdt)`, `when=not unfinished` --
    and stay amber until it does.

    Returns an mo.callout so the result renders in the cell, green/red/amber, in the style of
    mograder's student-facing check().
    """
    entries = [(None, v) for v in values] + list(named.items())
    if not when or all(is_unanswered(v) for _, v in entries):
        return mo.callout(
            mo.md("Waiting for your code: replace the `None` placeholders above."),
            kind="warn",
        )
    report, ok, blank = [], True, False
    for i, (label, value) in enumerate(entries, start=start):
        name = f"{key}_{i}"
        label = label or name
        if is_unanswered(value):
            blank = True
            report.append(f"`{label}` has not been filled in yet.")
            continue
        if name not in ANSWERS:
            report.append(f"`{label}` has no stored answer, skipping.")
            continue
        sol, shape, stride = reference_answer(name)
        ans = np.asarray(value)
        if ans.shape != shape:
            ok = False
            report.append(f"`{label}` has the wrong shape: expected `{shape}`, got `{ans.shape}`.")
            continue
        if stride > 1:
            ans = ans[tuple(slice(None, None, stride) for _ in range(ans.ndim))]
        finite = sol[np.isfinite(sol)] if sol.size else sol
        atol = 1e-3 * np.max(np.abs(finite)) if finite.size else 1e-8
        atol = float(atol) or 1e-8
        if np.allclose(ans, sol, atol=atol, equal_nan=True):
            report.append(f"`{label}` is correct.")
        else:
            ok = False
            report.append(
                f"`{label}` has the right shape but incorrect values:\n\n"
                f"```\n{diff_report(sol, ans, atol)}\n```"
            )
    body = "\n\n".join(f"- {line}" if "\n" not in line else line for line in report)
    if ok and blank:
        # Nothing is wrong, something is simply not there yet. Red would be a lie, and a
        # discouraging one: the reader has half an exercise right and is told it is a failure.
        return mo.callout(mo.md(f"**Still waiting.**\n\n{body}"), kind="warn")
    if ok:
        return mo.callout(mo.md(f"**Correct.**\n\n{body}"), kind="success")
    return mo.callout(mo.md(f"**Not quite yet.**\n\n{body}"), kind="danger")
