"""Convert one jupytext chapter from the TeachBooks book into a mystmd + marimo page.

Applies the port rules:

  Rule 1  solutions keep their own global chain, each binding versioned `<name>_sol<n>`, so a
          later solution can build on an earlier one without colliding with student stubs.
  Rule 2  a student global is versioned (`t_2`) only when a later exercise rebinds it; the first
          binder keeps the natural name, so chained reads still resolve.
  Rule 3  the 69 check-cell boilerplate blocks collapse to one ``check_answers(...)`` call with
          explicit arguments, so marimo can see the dependency (it builds its graph statically,
          and the original's ``eval(var)`` is invisible to it).
  Rule 4  stubs are normalised to *parse*, blanks are declared ``= None``,
          and the run of statements that would trip over an unfilled blank is indented under
          ``if <blank> is not None:``. marimo runs every cell on load, so an unfilled exercise
          -- and every later cell built on it -- must sit quietly rather than throw at the
          reader. Nothing uses ``mo.stop``: it propagates structurally, and takes the
          exercise's own answer check down with the cell.
  Rule 5  ``{exercise-start}`` / ``{solution-start}`` gating, since marimo cells cannot nest
          inside the plain directives.
  Rule 6  one ``{marimo-config}`` per page, carrying the imports, the answer bank and the
          checker in ``header:``. The plugin turns that into a marimo *setup cell*, which
          executes in the browser but is dropped from the rendered page -- machinery the reader
          never sees. It must be written as a ``---``-fenced YAML options block: the one-line
          ``:header: ...`` form does not parse block scalars (see NOTES.md).

Usage:
    .venv/bin/python scripts/convert_chapter.py Numerical_differentiation
    .venv/bin/python scripts/convert_chapter.py --all
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from dag_collisions import analyse
from oo_plots import convert_prose, to_object_oriented
from jb1_source import ANSWER_PREFIX, CHAPTERS, chapter_path, parse_chapter

ROOT = Path(__file__).resolve().parent.parent
ANSWERS_DIR = ROOT / "answers"

EXERCISE_RE = re.compile(r"\*\*Exercise\s+(?P<num>[0-9]+)\s*(?P<sub>\([a-z]\))?\s*:?\*\*", re.I)
SOLUTION_RE = re.compile(r"^\s*\*\*Solution:?\*\*\s*$", re.I | re.M)
SELFCHECK_RE = re.compile(r"\*\*Self check:?\*\*", re.I)
QUESTION_RE = re.compile(r'question\s*=\s*["\'](?P<q>answer_[0-9a-zA-Z_]+)["\']')
NUM_RE = re.compile(r"num\s*=\s*(?P<n>\d+)")
IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)")
ANCHOR_RE = re.compile(r"<a\s+href=(?P<q>[\"']?)(?P<url>[^\s>\"']+)(?P=q)\s*>(?P<text>.*?)</a>",
                       re.I | re.S)
OBJECTIVES_RE = re.compile(r"\*\*Learning objectives:?\*\*(?P<rest>.*)", re.I)
# a whole line that is just a parenthetical hint -- these read far better as an admonition
HINT_RE = re.compile(
    r"^\s*\*?\(?\s*Hint:\s*(?P<body>.+?)\)?\*?\s*$",
    re.I | re.M,
)


# --------------------------------------------------------------------------- markdown


def fix_math(text: str) -> str:
    """Wrap bare alignment math in \\begin{aligned} so KaTeX accepts it.

    MathJax tolerated `&=&` eqnarray style inside a bare `$$`; KaTeX does not. Blocks that
    already open an environment (\\begin{array}, \\begin{pmatrix}, ...) are left alone.
    """
    out: list[str] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].strip() == "$$":
            body: list[str] = []
            j = i + 1
            while j < len(lines) and lines[j].strip() != "$$":
                body.append(lines[j])
                j += 1
            if j < len(lines):
                blob = "\n".join(body)
                needs = ("&" in blob or "\\\\" in blob) and "\\begin{" not in blob
                if needs:
                    blob = blob.replace("&=&", "&=")
                    out.append("$$")
                    out.append("\\begin{aligned}")
                    out.append(blob.rstrip())
                    out.append("\\end{aligned}")
                    out.append("$$")
                else:
                    out.extend(["$$", *body, "$$"])
                i = j + 1
                continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


WIKI_URL = re.compile(r"https?://en\.wikipedia\.org/wiki/(?P<page>[^\s)\]\"`]+)")
NUMPY_OLD = re.compile(
    r"https?://docs\.scipy\.org/doc/numpy[^/]*/reference/(?P<path>[^\s)\]\"`]+)"
)
BARE_URL_LINE = re.compile(r"^[ \t]*(?P<url>https?://[^\s)\]]+)[ \t]*$", re.M)


def _wiki_target(page: str) -> str:
    """`[](wiki:Page)` renders the page title; an anchor has to be spelled out."""
    page = unquote(page.rstrip(".,"))
    if "#" in page:
        base, anchor = page.split("#", 1)
        label = anchor.replace("_", " ")
        return f"[{label}](wiki:{base}#{anchor})"
    return f"[](wiki:{page})"


def _doc_label(url: str) -> str:
    """Readable link text for an API doc URL: geomspace, fft.fftfreq, scipy.integrate.simps."""
    tail = url.rstrip("/").rsplit("/", 1)[-1]
    tail = re.sub(r"\.html(#.*)?$", "", tail)
    if tail.startswith("numpy."):
        return tail[len("numpy."):]
    if tail.startswith("routines."):
        return "numpy." + tail[len("routines."):]
    return tail


def fix_links(text: str) -> str:
    """Modernise and shorten the reference links the source book scattered as raw URLs."""
    # numpy moved off docs.scipy.org years ago; point at the stable docs
    text = NUMPY_OLD.sub(
        lambda m: f"https://numpy.org/doc/stable/reference/{m.group('path')}", text
    )

    # an existing markdown link to Wikipedia becomes the wiki: role
    text = re.sub(
        r"\[([^\]]*)\]\(" + WIKI_URL.pattern + r"\)",
        lambda m: f"[{m.group(1)}](wiki:{unquote(m.group('page'))})",
        text,
    )

    def bare(m: re.Match) -> str:
        url = m.group("url")
        w = WIKI_URL.fullmatch(url)
        if w:
            return _wiki_target(w.group("page"))
        if "numpy.org/doc" in url or "docs.scipy.org" in url:
            return f"[{_doc_label(url)}]({url})"
        return f"<{url}>"

    return BARE_URL_LINE.sub(bare, text)


def convert_markdown(text: str, figure_names: dict[str, int]) -> str:
    text = convert_prose(text)
    # after ANCHOR_RE: most of these references are raw <a href=...> in the source, so the
    # markdown-link rewrites below have nothing to match until the HTML is converted first
    text = ANCHOR_RE.sub(lambda m: f"[{m.group('text').strip()}]({m.group('url')})", text)
    text = fix_links(text)

    def image_sub(m: re.Match) -> str:
        src = Path(m.group("src")).name
        stem = re.sub(r"[^a-z0-9]+", "_", Path(src).stem.lower()).strip("_")
        figure_names[stem] = figure_names.get(stem, 0) + 1
        name = stem if figure_names[stem] == 1 else f"{stem}_{figure_names[stem]}"
        alt = m.group("alt").strip()
        caption = "" if alt in ("", "image") else alt
        block = [f":::{{figure}} ./figures/{src}", f":name: fig_{name}"]
        if caption:
            block.append("")
            block.append(caption)
        block.append(":::")
        return "\n".join(block)

    text = HINT_RE.sub(
        lambda m: ":::{hint}\n"
        + (lambda b: b[:1].upper() + b[1:])(m.group("body").strip())
        + "\n:::",
        text,
    )
    text = IMAGE_RE.sub(image_sub, text)
    # KaTeX does not know the Unicode prime; the book means f'(x)
    text = text.replace("\u2032", "'")
    text = fix_math(text)

    # "**Learning objectives:** After finishing ..." + following list -> admonition
    m = OBJECTIVES_RE.search(text)
    if m:
        before = text[: m.start()].rstrip()
        rest = text[m.end():]
        lines = rest.split("\n")
        body: list[str] = []
        k = 0
        # consume the intro sentence plus the numbered/bulleted list that follows
        while k < len(lines):
            ln = lines[k]
            if ln.strip() == "" and body and not any(
                l.strip().startswith(("1.", "2.", "3.", "4.", "5.", "-", "*")) for l in lines[k + 1:k + 3]
            ):
                break
            body.append(ln)
            k += 1
        after = "\n".join(lines[k:])
        adm = [":::{admonition} Learning goals", ":class: tip", ""]
        adm += [l for l in "\n".join(body).strip().split("\n")]
        adm += [":::"]
        text = f"{before}\n\n" + "\n".join(adm) + "\n" + after
    return text


def split_markdown(text: str) -> list[tuple[str, str]]:
    """Split one markdown block into ``(kind, text)`` segments.

    The source pairs prose and exercises in the same block (jupytext only breaks a block at a
    code fence), so "## Introduction ... **Exercise 1:** do the thing" arrives as a single
    chunk. Emitting an exercise gate around the whole thing would wrap the chapter's prose in
    exercise 1, and would swallow the preceding "**Self check:**" list into the next exercise.
    """
    marks: list[tuple[int, int, str]] = []
    for m in EXERCISE_RE.finditer(text):
        marks.append((m.start(), m.end(), "exercise"))
    for m in SELFCHECK_RE.finditer(text):
        marks.append((m.start(), m.end(), "selfcheck"))
    if not marks:
        return [("prose", text)] if text.strip() else []

    marks.sort()
    segments: list[tuple[str, str]] = []
    head = text[: marks[0][0]].strip()
    if head:
        segments.append(("prose", head))
    for idx, (_start, end, kind) in enumerate(marks):
        stop = marks[idx + 1][0] if idx + 1 < len(marks) else len(text)
        body = text[end:stop].strip()
        if not body:
            continue
        if kind == "selfcheck":
            # a self check is just the bullet list that follows; everything after it is ordinary
            # prose belonging to the next section, and putting it inside the admonition swallowed
            # 64 lines of Linear_algebra -- including a figure and the next exercise's set-up
            checklist, rest = _leading_list(body)
            segments.append((kind, checklist))
            if rest:
                segments.append(("prose", rest))
        else:
            segments.append((kind, body))
    return segments


STRUCTURAL = re.compile(r"^(#{1,6}\s|:{3,}|\$\$|!\[|```)")


def fence_for(body: str) -> str:
    """A directive fence one colon longer than the longest fence it must contain.

    MyST nests by fence length, so a `:::{hint}` inside a `:::{tip}` silently mis-parses --
    the self check needs `::::` once a hint is folded into it.
    """
    longest = max((len(m) for m in re.findall(r"^:{3,}", body, re.M)), default=2)
    return ":" * max(3, longest + 1)


def _leading_list(text: str) -> tuple[str, str]:
    """Split a self check off from the prose that follows it.

    A self check is its bullet list *plus* any short prose that belongs with it -- several
    exercises end with "What do you see in the plot?" or a parenthetical hint, which read as part
    of the check. Consumption stops at the first structural element (a heading, directive,
    display math, image or code fence), which is where the next section really begins; without
    that stop the admonition swallowed 64 lines of Linear_algebra.
    """
    lines = text.split("\n")
    end = _list_end(lines)
    # keep following plain paragraphs, but never cross a structural boundary
    i = end
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if STRUCTURAL.match(stripped):
            break
        end = i + 1
        i += 1
    return "\n".join(lines[:end]).strip(), "\n".join(lines[end:]).strip()


def _list_end(lines: list[str]) -> int:
    end = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("*", "-", "+")) or re.match(r"^\d+[.)]\s", stripped):
            end = i + 1
        elif not stripped:
            continue
        else:
            break
    return end


# --------------------------------------------------------------------------- code


def rename_locals(source: str, names: set[str]) -> str:
    """Underscore-prefix the given top-level names so marimo treats them as cell-local."""
    for n in sorted(names, key=len, reverse=True):
        source = re.sub(rf"\b{re.escape(n)}\b", f"_{n}", source)
    return source


def loop_only_names(source: str) -> set[str]:
    """Names this cell binds *only* as a `for` target.

    Loops do not create a scope, so `for i in range(N)` binds a cell-scope `i` -- and PDE1 has
    six cells doing exactly that. Versioning them would litter the exercises with `i_3`, `j_5`;
    underscoring makes them cell-local, which is both marimo-idiomatic and what a reader expects
    a loop counter to be.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    loop: set[str] = set()
    other: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            loop |= {
                n.id for n in ast.walk(node.target)
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
            }
    for name in _bound(source):
        if name not in loop:
            other.add(name)
    return loop - other


def transform_stub(source: str, versions: dict[str, str], seen: dict[str, int]) -> str:
    """Rule 2 (revised): version a student global only when a later exercise rebinds it.

    The chapters reuse scratch names across independent exercises -- `h` in exercises 2 and 3,
    `N` in 4 and 5, `t` in 5 and 8 -- which marimo rejects outright.

    Underscoring every collision would be wrong: `t` is genuinely *chained*, defined in exercise
    5 and read by 6 and 7 before exercise 8 rebinds it. So the first cell to bind a name keeps
    the natural spelling, later rebindings become `t_2`, `t_3`, and subsequent reads follow the
    latest version. Students see plain `x`, `t`, `h` almost everywhere, and the chain stays
    intact.
    """
    bound = {
        n for n in _bound(source)
        if n not in PROTECTED and not n.startswith("_") and not n.startswith("answer_")
    }
    counters = loop_only_names(source)
    mapping = dict(versions)
    for name in sorted(counters):
        mapping[name] = f"_{name}"
    for name in sorted(bound - counters):
        if name in seen:
            seen[name] += 1
            mapping[name] = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
            mapping[name] = name
    src = _retoken(source, mapping, before=dict(versions))
    for name in bound - counters:
        versions[name] = mapping.get(name, name)
    return src


def normalise_stub(source: str) -> str:
    """Make a stub parse. Empty function/loop bodies get `...`; that is all that is needed."""
    if _parses(source):
        return source
    lines = source.split("\n")
    out: list[str] = []
    opener = re.compile(r"^(\s*)(def |class |for |while |if |elif |else|try|except|with )")
    for idx, ln in enumerate(lines):
        out.append(ln)
        m = opener.match(ln)
        if m and ln.rstrip().endswith(":"):
            indent = len(m.group(1))
            nxt = next((l for l in lines[idx + 1:] if l.strip() and not l.strip().startswith("#")), None)
            if nxt is None or (len(nxt) - len(nxt.lstrip())) <= indent:
                filler = "return None" if m.group(2) == "def " else "..."
                out.append(" " * (indent + 4) + filler)
    fixed = "\n".join(out)
    return fixed if _parses(fixed) else source


def has_unfinished_loop(source: str) -> bool:
    """True if a `while` loop's body is still a placeholder -- i.e. it cannot terminate.

    PDE1's relaxation exercises are shipped as `while delta_max > target_accuracy:` with the
    body commented out. `normalise_stub` fills that body with `...`, so nothing ever updates
    `delta_max` and the loop spins forever -- it hung the build, and it would equally hang a
    student's browser tab, because marimo runs every cell on load.

    The `None`-placeholder guard does not catch this: the cell assigns `delta_max = 1` further
    down, so by the time the guard runs the value is no longer None.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.While):
            continue
        condition = {
            n.id for n in ast.walk(node.test)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
        }
        assigned = {
            n.id for stmt in node.body for n in ast.walk(stmt)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
        }
        breaks = any(isinstance(n, ast.Break) for stmt in node.body for n in ast.walk(stmt))
        if condition and not (condition & assigned) and not breaks:
            return True
    return False


# A `while` loop whose exit condition the student still has to write cannot terminate, and would
# hang the build and the reader's browser alike. `unfinished` holds it back until they say so.
# It is a real, visible switch rather than an `mo.stop`, because `mo.stop` takes the exercise's
# own answer check down with it (descendants of a stopped cell are never run).
UNFINISHED_NOTE = (
    "# Set `_unfinished` to False once you have written the code below, so that it can run.\n"
    "_unfinished = True\n"
)


def _parses(src: str) -> bool:
    try:
        ast.parse(src)
        return True
    except SyntaxError:
        return False


# Imports that must never survive the port: the answer-checker is now inlined, micropip is
# implicit under marimo's WASM runtime, and ipywidgets is replaced by marimo's own UI elements.
DROP_IMPORT = re.compile(r"validate_answers|micropip|ipywidgets|IPython")


def collect_imports(blocks) -> list[str]:
    """Union of every top-level import in the chapter, deduped and ordered.

    marimo forbids a global being bound by two cells, and `import numpy as np` binds `np`. The
    source book re-imports numpy and matplotlib in most cells, so every import is hoisted into
    the page header instead and stripped from the cells (see `strip_imports`).
    """
    seen: dict[str, None] = {}
    for b in blocks:
        if b.kind != "code" or b.is_init:
            continue
        for line in b.source.split("\n"):
            s = line.strip()
            if not (s.startswith("import ") or s.startswith("from ")):
                continue
            if DROP_IMPORT.search(s) or not _parses(s):
                continue
            seen.setdefault(s, None)
    return list(seen)


# Bugs in the source book that newer numpy/matplotlib turn from warnings into errors. Verified
# by running the *original* solution cells unmodified: they fail identically there, so these are
# pre-existing defects, not porting damage.
CONTENT_FIXES: dict[str, list[tuple[str, str]]] = {
    # `sol.t_events[0]` is the array of times an event fired, not a scalar. Printing it with %f
    # raises "only 0-dimensional arrays can be converted to Python scalars", and assigning it
    # into `tf1[i]` raises "setting an array element with a sequence". The book itself uses the
    # correct `sol.t_events[0][0]` elsewhere, so this is simply inconsistent.
    "Ordinary_differential_equations_2": [
        (r"sol\.t_events\[0\](?!\[)", "sol.t_events[0][0]"),
    ],
    # a bare prose line sitting in a code cell -- a SyntaxError, and the cell never ran
    "Random_numbers": [
        (r"^(\s*)Your code here:\s*$", r"\1# Your code here"),
    ],
    # matplotlib now rejects a list-valued `label=` for a single dataset:
    # "label must be scalar or have the same length as the input data".
    "Linear_algebra": [
        (r"label=\['mode (\d): omega\^2=', str\((omega\d\*\*2)\)\]",
         r"label='mode \1: omega^2=' + str(\2)"),
    ],
}


# Cells that describe the *old delivery platform* rather than the physics. They assume a
# JupyterHub workspace with a filesystem and an upload button; this book runs in the browser,
# where neither exists. Dropped whole, with the surrounding prose rewritten in PROSE_FIXES.
DROP_CELLS: dict[str, list[str]] = {
    "Linear_algebra": ['Image(filename="my_derivation.jpg")'],
}


# Prose that referred to the old platform. Kept deliberately small: this is a *port*, and
# rewriting content is a separate pass. Each entry exists because the text is now false, not
# because it could be better.
PROSE_FIXES: dict[str, list[tuple[str, str]]] = {
    # Exercise 5 asked students to photograph a pen-and-paper derivation and upload the JPG to
    # their workspace, then render it with `IPython.display.Image`. There is no workspace, no
    # upload button and no filesystem here. The derivation itself is the point of the exercise
    # and is kept; only the hand-in mechanics go.
    "Linear_algebra": [
        (
            r"Take a picture of your derivation and upload it to your workspace as a JPG file\s*"
            r"named `my_derivation\.jpg` using the \"upload\" button that is visible in the top\s*"
            r"right of the screen in your workspace:\s*\n+"
            r"!\[image\]\(upload_button\.png\)\s*\n+"
            r"After you upload the image, the image should be displayed here inline if you run\s*"
            r"the following code:",
            "Keep the derivation next to you -- you will need the matrix you wrote down in the "
            "next cell.",
        ),
    ],
}


def apply_prose_fixes(text: str, chapter: str) -> str:
    for pattern, replacement in PROSE_FIXES.get(chapter, []):
        text = re.sub(pattern, replacement, text)
    return text


def is_dropped(source: str, chapter: str) -> bool:
    return any(marker in source for marker in DROP_CELLS.get(chapter, []))


def drop_cells(blocks: list, chapter: str) -> list:
    """Remove DROP_CELLS, rejoining the prose that surrounded them.

    A markdown block that follows an exercise closes it, so leaving the two paragraphs either
    side of a dropped cell as separate blocks ended Linear Algebra's exercise 5 after its first
    sentence, with the Python half of the same exercise outside it. The cell is gone; the prose
    on both sides of it is one passage again.
    """
    if not DROP_CELLS.get(chapter):
        return blocks
    out: list = []
    just_dropped = False
    for block in blocks:
        if block.kind == "code" and is_dropped(block.source, chapter):
            just_dropped = True
            continue
        if just_dropped and out and block.kind != "code" and out[-1].kind != "code":
            out[-1].source = f"{out[-1].source.rstrip()}\n\n{block.source.lstrip()}"
            just_dropped = False
            continue
        just_dropped = False
        out.append(block)
    return out


# The book's one `ipywidgets.interact` exercise. marimo's UI elements replace it, but they only
# become reactive when the element is defined in one cell and read in another -- so this cell has
# to become two. Names are the source's originals; the usual renaming passes run afterwards.
#
# This is also the clearest win of the whole port: the original text apologises for its own
# widget ("The update is not super-fast: it is best to select the slider and use the arrow keys").
SLIDER_CELLS = [
    """# Sliders for the zoom level and the colour scale.
zoom = mo.ui.slider(20, 1000, step=10, value=1000, label="Zoom (pixels)")
v_index = mo.ui.slider(1, 19, step=1, value=19, label="Colour scale")
mo.hstack([zoom, v_index])""",
]

SPLIT_CELLS: dict[str, list[tuple[str, bool, list[str]]]] = {
    "Fourier_transforms_2": [
        (
            "interact(update,",
            False,
            SLIDER_CELLS
            + [
                """# To really be able to tweak the colormap over a large range,
# we will make an array of maximum colour values that is geometrically spaced
N = 20
vmax_array = np.geomspace(1e1, 6e7, N)
vmax = vmax_array[v_index.value]

# Show the central `zoom.value` pixels of the diffraction pattern.
# start = ...
# end = ...
# k_zoom = ...
# exts = ...
# _fig, _ax = plt.subplots(figsize=(8, 8))
# ..."""
            ],
        ),
        (
            "interact(update",
            True,
            SLIDER_CELLS
            + [
                """# To really be able to tweak the colormap over a large range,
# we will make an array of maximum colour values that is geometrically spaced
N = 20
vmax_array = np.geomspace(1e1, 6e7, N)
vmax = vmax_array[v_index.value]

start = int(len(x) / 2 - zoom.value / 2)
end = start + zoom.value
k_zoom = k_max * zoom.value / len(x)
exts = [-k_zoom, k_zoom, -k_zoom, k_zoom]

_fig, _ax = plt.subplots(figsize=(8, 8))
plt.imshow(diffraction_pattern[start:end, start:end], extent=exts, vmax=vmax)
plt.xlabel("k$_x$ (nm$^{-1}$)")
plt.ylabel("k$_y$ (nm$^{-1}$)")
plt.colorbar()"""
            ],
        ),
    ],
}


def split_for(source: str, chapter: str, is_solution: bool) -> list[str] | None:
    for marker, for_solution, replacement in SPLIT_CELLS.get(chapter, []):
        if marker in source and for_solution == is_solution:
            return replacement
    return None


LOADTXT_RE = re.compile(r"np\.loadtxt\(\s*([\"'])(?P<name>[^\"']+)\1")


def apply_content_fixes(source: str, chapter: str) -> str:
    for pattern, replacement in CONTENT_FIXES.get(chapter, []):
        source = re.sub(pattern, replacement, source, flags=re.M)
    # a bare filename cannot resolve in the browser; route it through load_data()
    source = LOADTXT_RE.sub(lambda m: f'load_data("{m.group("name")}"', source)
    return source


def python_literal(mapping: dict, width: int = 4000) -> str:
    """Render the answer bank as Python source, wrapped so no line is enormous.

    Two constraints meet here. It must be *Python*, not JSON -- `json.dumps` writes `true`, and
    the downsampled entries carry a boolean flag. And no line may be huge: emitted as a single
    1.48 MB line, mystmd failed to read the page at all with
    `SyntaxError: Unterminated string in JSON at position 1114112`.

    `pprint.pformat` fixes the line length but more than doubles the payload in indentation, so
    the literal is wrapped by hand at comma boundaries. Newlines inside brackets are implicit
    line joins, so the result stays a valid literal.
    """
    lines = ["{"]
    for key, value in mapping.items():
        text = repr(value)
        if len(text) <= width:
            lines.append(f"{key!r}: {text},")
            continue
        chunks, start = [], 0
        while start < len(text):
            if start + width >= len(text):
                chunks.append(text[start:])
                break
            cut = text.find(",", start + width)
            if cut == -1:
                chunks.append(text[start:])
                break
            chunks.append(text[start : cut + 1])
            start = cut + 1
        lines.append(f"{key!r}: " + "\n".join(chunks) + ",")
    lines.append("}")
    return "\n".join(lines)


def imported_names(statements: list[str]) -> set[str]:
    """Names the hoisted header imports bind.

    Parsed rather than split on whitespace: `from numpy import array,empty` has no space after
    the comma, so a naive `.split()[-1]` yields the single token `array,empty`. `empty` then
    looked undefined, earned a `None` placeholder, and collided with the import itself --
    `MultipleDefinitionError(name='empty')`.
    """
    names: set[str] = set()
    for stmt in statements:
        try:
            tree = ast.parse(stmt)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    names.add(alias.asname or alias.name.split(".")[0])
    return names


def strip_imports(source: str) -> str:
    """Remove top-level imports and IPython magics; the page header now owns the imports.

    `%%capture` (4 cells in PDE2, used to hide the static frame of a FuncAnimation) is not valid
    Python, so those cells failed to parse and were skipped by every later transform. marimo has
    no cell magics and renders the last expression, so dropping the line is both necessary and
    sufficient.
    """
    out = []
    for line in source.split("\n"):
        s = line.strip()
        if (s.startswith("import ") or s.startswith("from ")) and _parses(s):
            continue
        if "await micropip.install" in s:
            continue
        if s.startswith("%"):  # %%capture, %matplotlib, ...
            continue
        out.append(line)
    return "\n".join(out).strip("\n")


SENTINEL_RE = re.compile(r"^\s*###\s*(BEGIN|END)\s+SOLUTIONS?\s*$\n?", re.M | re.I)

# `# ...` is filler marking "your code goes here". `normalise_stub` already puts a real `...` in
# the body, so the comment is noise -- `def f(x): ...` says it better.
FILLER_RE = re.compile(r"^[ \t]*#[ \t]*\.\.\.[ \t]*$\n?", re.M)

# `# yd_analytical = ` and `# fwd_derv = np.zeros(_____)` are blanks for the student to fill in.
# They belong in a stub; in a *solution* they sit directly above the real answer, which reads as
# duplication -- and they were being SSA-renamed too (`# yd_analytical_sol2 = `).
HINT_ASSIGN_RE = re.compile(r"^[ \t]*#[ \t]*([A-Za-z_]\w*(?:[ \t]*\[.*\])?)[ \t]*=(?!=)(.*)$")
BLANK_MARK_RE = re.compile(r"_{2,}|\.{2,}")


def is_stub_hint(line: str) -> bool:
    """A commented assignment that is a *blank*, as opposed to commented-out real code.

    The distinction matters only in solutions, where a blank is duplication sitting above the
    real answer but a commented line the author wrote ("#x=a+(b-a)*np.random.rand(N)", an
    alternative one-liner) is content. A blank always shows its gap: an empty right-hand side, or
    a run of dots or underscores standing in for what the reader must supply -- and the gap can
    be in the subscript rather than the value (`# rho_fixed[___,___] = 1`, `# V[0] = ____`).
    """
    m = HINT_ASSIGN_RE.match(line)
    if not m:
        return False
    target, rhs = m.group(1), m.group(2).strip()
    if rhs == "" or set(rhs) <= set("._ "):
        return True
    return bool(BLANK_MARK_RE.search(target) or BLANK_MARK_RE.search(rhs))


SETUP_ONLY = re.compile(r"^\s*(?:#|plt\.rcParams\b|import\b|from\b|$)")


def is_setup_cell(source: str) -> bool:
    """A cell that only configures the session -- imports, rcParams, comments.

    The book opens each chapter with one ("I like bigger plots: setting a higher DPI makes the
    fonts bigger"). It is not an exercise and there is nothing in it for a reader to change, so
    it is hoisted into the page header along with the imports and never rendered at all.
    """
    lines = [ln for ln in source.split("\n") if ln.strip()]
    return bool(lines) and all(SETUP_ONLY.match(ln) for ln in lines)


def is_session_setup(original: str) -> bool:
    """The chapter's opening configuration cell, as it appears in the source.

    `is_setup_cell` alone is not enough to decide this: it also accepts a cell of pure comments,
    and the book's empty scratch cells are exactly that -- `# Your code here:` and nothing else.
    Hoisting those deleted eleven exercises from the book and buried their prompts in the page
    header. What separates the two is that real setup carries imports or an rcParams line; a
    scratch cell carries neither, and belongs on the page with an editor.
    """
    if not is_setup_cell(original):
        return False
    body = strip_imports(original)
    had_imports = body != original
    return had_imports or any(
        ln.strip().startswith("plt.rcParams") for ln in body.split("\n")
    )


def collect_setup(blocks) -> list[str]:
    """Session configuration hoisted out of the page and into `{marimo-config}`'s header.

    Only the statements: the comment that introduced them ("I like bigger plots...") was written
    for a reader looking at the cell, and there is no cell any more.
    """
    out: list[str] = []
    for b in blocks:
        if b.kind != "code" or b.is_init or b.is_check or b.is_solution:
            continue
        if not is_session_setup(b.source):
            continue
        body = "\n".join(
            ln for ln in strip_imports(b.source).split("\n") if not ln.strip().startswith("#")
        ).strip()
        if body:
            out.append(body)
    return out


# Scaffolding that names no variable: `# V[0] = ____`, `#delta[i,j] = ...`. The book uses it for
# blanks that are *elements* of an array the cell has already allocated, so there is nothing to
# declare as None and nothing to test -- see `unfinished`.
ELEMENT_BLANK_RE = re.compile(r"^\s*#\s*[A-Za-z_]\w*\s*\[[^\]]*\]\s*=(?!=)", re.M)


def _loads(stmt: ast.AST) -> set[str]:
    return {
        n.id for n in ast.walk(stmt)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    }


def _loaded(source: str) -> set[str]:
    """Every name a cell reads at top level (function bodies excluded, as ever)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    out: set[str] = set()
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        out |= _loads(stmt)
    return out


def stub_fns(source: str) -> tuple[str, ...]:
    """Placeholder functions the cell defines, whether or not it calls them.

    A cell that still contains `def dVdt(t, V): return None` is unfinished by definition, even
    when nothing in the cell calls it -- ODE1 is eight exercises of exactly that shape. Left
    unguarded, `V = np.empty(N)` followed by `answer_11_2_1 = np.copy(V)` handed the checker a
    copy of uninitialised memory, which is a far worse failure than an error: it looks like an
    answer, and the reader gets a confident diff against numbers they never produced.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ()
    return tuple(n.name for n in tree.body if _is_placeholder_def(n))


def element_blank_line(source: str) -> int | None:
    """Line of the first `# V[0] = ____` / `#delta[i,j] = ...` scaffolding, if any."""
    m = ELEMENT_BLANK_RE.search(source)
    return source[: m.start()].count("\n") + 1 if m else None


def empty_loop_line(source: str) -> int | None:
    """Line of the first top-level loop whose body the student has still to write.

    `for i in range(Ni):` with a body of `...` is the book's own "your code here", and the loop
    around it is real code that runs. ODE2 9.8 spun two such loops over `tf1 = np.empty(Ni)` and
    handed the checker the uninitialised result.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for stmt in tree.body:
        if not isinstance(stmt, (ast.For, ast.While)):
            continue
        body = [s for s in ast.walk(stmt) if isinstance(s, ast.stmt)]
        real = [
            s for s in body
            if not isinstance(s, (ast.For, ast.While, ast.If))
            and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
        ]
        if not real:
            return stmt.lineno
    return None


def unfinished_line(source: str, blanks: tuple[str, ...], defeated: set[str]) -> int | None:
    """Where to start the `_unfinished` guard, for a cell with nothing testable to gate on.

    Some exercises have no blank that can be named: the student fills in the elements of an array
    the cell allocated, or the body of a loop the cell already runs. There is no variable to
    compare against None, so those cells carry a switch the reader turns off themselves. Only
    reached when the cell really has nothing else -- a blank or an unwritten function is always
    the better gate, because it needs no action of its own.
    """
    if blanks or stub_fns(source):
        return None
    lines = [
        element_blank_line(source),
        empty_loop_line(source),
    ]
    if defeated:
        for name in sorted(defeated):
            m = re.search(rf"^\s*#\s*{re.escape(name)}\s*=", source, re.M)
            if m:
                lines.append(source[: m.start()].count("\n") + 1)
    found = [ln for ln in lines if ln]
    return min(found) if found else None


def guard_start(
    source: str,
    names: tuple[str, ...],
    *,
    unfinished: bool = False,
    from_line: int | None = None,
) -> int | None:
    """Index of the first top-level statement that must not run while a blank is unfilled.

    Everything from there to the end of the cell is guarded together, as one contiguous run.
    Splitting statements into "safe" and "unsafe" groups and reordering them -- which is what
    the old `def _plot()` wrapper did -- tore the scaffolding comments away from the code they
    annotate, and produced cells like FT1's exercise 10, where `#if ____ > ____:` ended up
    orphaned inside the display function at the wrong indentation.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    wanted = set(names)
    stubs = set(stub_fns(source))
    last_stub = max(
        (k for k, s in enumerate(tree.body) if getattr(s, "name", None) in stubs),
        default=None,
    )
    for k, stmt in enumerate(tree.body):
        # a def/class body does not run until it is called, so a blank read there is fine
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        # a loop whose exit condition the student has still to write cannot terminate, so it and
        # everything after it must sit inside the guard
        if unfinished and isinstance(stmt, ast.While):
            return k
        # scaffolding that names no variable: guard the statement it sits inside
        if from_line is not None and (stmt.end_lineno or stmt.lineno) >= from_line:
            return k
        # An answer computed after an unwritten function is downstream of it whether or not it
        # calls it -- ODE1's `answer_11_2_1 = np.copy(V)` on an array the missing function was
        # supposed to fill. Only the answer lines: the statements between are the book's own
        # given constants (`x0 = 1`, `h = 0.5`), and guarding those left them None.
        if last_stub is not None and k > last_stub and _is_answer_assign(stmt):
            return k
        if _loads(stmt) & wanted:
            return k
    return None


def _is_answer_assign(stmt: ast.AST) -> bool:
    return isinstance(stmt, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id.startswith("answer_") for t in stmt.targets
    )


# Names the guarded region may bind that the cell still has to define even when the guard does
# not run: marimo makes every one of them a page global, and a later cell reading an undefined
# global fails outright rather than politely. Cell-local names (a leading underscore) need it
# only when the trailing `show(...)` reads them -- which is just the axes.
def _hoisted(names: set[str], displayed: str | None) -> list[str]:
    keep = {n for n in names if not n.startswith("_")}
    if displayed and displayed.startswith("_") and displayed in names:
        keep.add(displayed)
    return sorted(keep)


def guard_unset(
    source: str,
    blanks: tuple[str, ...],
    *,
    displayed: str | None = None,
    triggers: tuple[str, ...] = (),
    unfinished: bool = False,
    from_line: int | None = None,
) -> tuple[str, list[str]]:
    """Indent the tail of a stub under `if <blank> is not None:`.

    A marimo page runs every cell the moment it loads, so an unfilled exercise executes too --
    and so does every later cell that reads what it was supposed to define. Without this, FT1
    opened on eight tracebacks, none of them the reader's fault: exercise 1 defines `t`, `y` and
    `fs`, and the rest of the chapter is built on them.

    Guarded, the page loads clean, each cell says which blank it is waiting for, and filling in
    exercise 1 brings the rest of the chapter to life at once -- which is the reactive model the
    book is trying to teach, demonstrated rather than described.

    This also replaces the `mo.stop` that used to hold back a not-yet-terminating loop. `mo.stop`
    worked, but it propagates *structurally*: every descendant of a stopped cell is marked
    "ancestor stopped" and can never run, so the exercise's own answer check died with it. An
    `if` only skips the statements it encloses.
    """
    stubs = stub_fns(source)
    # `triggers` are names that make a statement unsafe without themselves being testable:
    # calling `calc_u()` fails because of the blanks *inside* it, which is what the
    # condition tests, but it is the call that has to be spotted.
    start = guard_start(
        source, blanks + stubs + triggers, unfinished=unfinished, from_line=from_line
    )
    if start is None:
        return source, []
    tree = ast.parse(source)
    lines = source.split("\n")
    # A figure created just above the guarded plotting belongs inside it too, or the reader gets
    # an empty axes box where the guard's message should be.
    while start > 0 and _bound_in(tree.body[start - 1]) & {"_fig", "_ax", "_axs"}:
        start -= 1
    # Line ranges, not ast.get_source_segment: a statement's segment excludes the comments
    # around it, and in this book the scaffolding is mostly comments.
    split = (tree.body[start].lineno - 1) if start < len(tree.body) else len(lines)
    # take any comment block immediately above the first guarded statement with it
    while split > 0 and lines[split - 1].lstrip().startswith("#"):
        split -= 1
    head, tail = lines[:split], lines[split:]
    while head and not head[-1].strip():
        head.pop()
    while tail and not tail[-1].strip():
        tail.pop()
    if not tail:
        return source, []

    # `# xsol = ...` is where the book tells the student to write, so it cannot be left inside
    # the guard: anything written there is invisible to the `if` above it, and the cell would
    # sit saying "waiting for xsol" however carefully they filled it in. The hints move up to
    # just above the guard, beside the placeholder they belong to.
    # Only unindented hints move. One nested inside a loop body belongs to that loop -- PDE1's
    # `#delta_max =....` sits inside the iteration whose exit condition it describes -- and
    # lifting it out stranded it at top level, still wearing its indentation.
    wanted = set(blanks)
    hints = [
        ln for ln in tail
        if not ln[:1].isspace()
        and (m := COMMENTED_ASSIGN_RE.match(ln))
        and m.group(1) in wanted
    ]
    tail = [ln for ln in tail if ln not in hints]

    # Only names the guard *alone* binds need a value for when it does not run. A name the head
    # already set keeps that value -- hoisting `phi = np.zeros([M, M])` back to None would throw
    # away work the cell had legitimately done.
    head_bound = set()
    for stmt in tree.body[:start]:
        head_bound |= _bound_in(stmt)
    bound = set()
    for stmt in tree.body[start:]:
        bound |= _bound_in(stmt)
    # loop variables become cell-local `_i`/`_j` in the renaming pass that runs after this one
    hoist = _hoisted(bound - head_bound - loop_only_names(source), displayed)

    # `given(...)` covers both kinds of blank: a value is tested against None, a function against
    # its placeholder body. Spelled out as `a is not None and b is not None and ...` this was
    # five lines of wrapped boilerplate above every exercise.
    waited_on = list(dict.fromkeys([*blanks, *stubs]))
    terms = ["not _unfinished"] if unfinished else []
    if waited_on:
        terms.append(f"given({', '.join(waited_on)})")
    guard = f"if {' and '.join(terms)}:"
    if len(guard) > 88:
        wrapped = ",\n    ".join(waited_on)
        terms[-1] = f"given(\n    {wrapped},\n)"
        guard = f"if {' and '.join(terms)}:"

    block = [*head]
    if head:
        block.append("")
    if unfinished:
        block.append(UNFINISHED_NOTE)
    if hints:
        block.extend([*hints, ""])
    if hoist:
        block.append(" = ".join(hoist) + " = None")
    block.append(guard)
    block.extend(f"    {ln}" if ln.strip() else "" for ln in tail)
    # lifting the hints out leaves a gap where each one stood
    return re.sub(r"\n{3,}", "\n\n", "\n".join(block)), hoist


def functions_needing(source: str, unset: set[str]) -> dict[str, set[str]]:
    """Functions this cell defines whose *body* reads a still-unfilled global.

    PDE2 exercise 3 has the student write `def calc_u(t): return my_idst(uk)`, where `uk` is one
    of that exercise's blanks. The function is defined perfectly happily; it is *calling* it, two
    exercises later, that fails. So being unfilled has to travel through the function: a cell
    that calls `calc_u` needs the same guard as one that reads `uk` directly.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    out: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        local = {a.arg for a in node.args.args} | _bound_in(ast.Module(body=node.body, type_ignores=[]))
        needs = {
            n.id for n in ast.walk(node)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
        } & unset - local
        if needs:
            out[node.name] = needs
    return out


def _bound_anywhere(source: str) -> set[str]:
    """Every name the cell binds at cell scope, guarded or not."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    out: set[str] = set()
    for stmt in tree.body:
        out |= _bound_in(stmt)
    return out


def _bound_outside_guard(source: str) -> set[str]:
    """Names bound by statements that run unconditionally, ignoring the placeholder line.

    `x = y = None` binds `x` and `y` too, but binding them to None is the very thing that makes
    them unfilled, so it must not count as filling them in.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    out: set[str] = set()
    for stmt in tree.body:
        if isinstance(stmt, ast.If):
            continue
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Constant) \
                and stmt.value.value is None:
            continue
        out |= _bound_in(stmt)
    return out


def _bound_in(stmt: ast.AST) -> set[str]:
    """Names a statement binds at cell scope (function and class bodies excepted)."""
    out: set[str] = set()
    stack = [stmt]
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
            continue
        if isinstance(node, (ast.Lambda, ast.GeneratorExp, ast.ListComp, ast.SetComp,
                             ast.DictComp)):
            continue
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            out.add(node.id)
        stack.extend(ast.iter_child_nodes(node))
    return out


def answer_sources(source: str) -> tuple[str, ...]:
    """The variables a solution's `answer_* = ...` lines are built from.

    `answer_4_02_1 = trapezoidal_integral` and `answer_7_01_1 = np.copy(t)` both name something
    the reader cares about; the `answer_*` key itself is bookkeeping and means nothing to them.
    Anything more involved than a name or a copy of one is skipped rather than guessed at.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ()
    out: list[str] = []
    for stmt in tree.body:
        if not _is_answer_assign(stmt):
            continue
        value = stmt.value
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) \
                and value.func.attr == "copy" and len(value.args) == 1:
            value = value.args[0]
        elif isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) \
                and value.func.attr == "copy" and not value.args:
            value = value.func.value
        if isinstance(value, ast.Name) and value.id not in out:
            out.append(value.id)
    return tuple(out)


def adopt_trailing_display(source: str, tail: str | None) -> tuple[str, str | None]:
    """Hand a cell's own final expression to `show(...)` instead of leaving it dangling.

    marimo renders a cell's last expression, so `mo.hstack([...])` or `np.sum(answer)` on the
    last line *was* the cell's output -- until `show(...)` was appended below it and became the
    last expression instead, silently swallowing it. Those expressions are moved into the call.

    `fig.show()` is the same case in disguise: it returns None, and under islands it draws
    nothing at all, so the figure itself is what should be displayed.
    """
    if tail is not None:
        return source, tail
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, None
    if not tree.body or not isinstance(tree.body[-1], ast.Expr):
        return source, None
    stmt = tree.body[-1]
    expr = stmt.value
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in {
        "show", "print",
    }:
        return source, None
    text = ast.unparse(expr)
    # `fig.show()` -> display `fig`
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
            and expr.func.attr == "show" and not expr.args:
        text = ast.unparse(expr.func.value)
    lines = source.split("\n")
    del lines[stmt.lineno - 1: (stmt.end_lineno or stmt.lineno)]
    return "\n".join(lines).rstrip(), text


def show_call(first: str | None, blanks: tuple[str, ...], width: int = 88) -> str:
    """The last line of a cell: its output, and therefore its play button."""
    parts = ([first] if first else []) + [f"{b}={b}" for b in blanks]
    single = f"show({', '.join(parts)})"
    if len(single) <= width:
        return single
    body = "\n".join(f"    {p}," for p in parts)
    return f"show(\n{body}\n)"


def strip_scaffold_comments(source: str, *, solution: bool) -> str:
    """Drop the fill-in-the-blank scaffolding a cell no longer needs."""
    source = FILLER_RE.sub("", source)
    if solution:
        source = "\n".join(ln for ln in source.split("\n") if not is_stub_hint(ln))
    return re.sub(r"\n{3,}", "\n\n", source)

# Names the renaming passes must never touch: the page header's imports, the inlined checker's
# own globals, and builtins. Loop variables are deliberately absent -- a top-level `for i in ...`
# binds a global `i`, so two solutions both owning `i` really is a collision.
PROTECTED = {
    "np", "mo", "plt", "ANSWERS", "check_answers", "reference_answer", "to_array",
    "diff_report", "is_unanswered", "preview", "describe", "load_data", "DATA_URL",
    "show", "print", "drain_printed", "PRINTED", "written", "last_write",
    "unwritten_stub", "format_printed", "answer_sources", "range", "len", "enumerate", "zip", "abs",
    "min", "max", "sum", "float", "int", "str", "list", "dict", "tuple", "set", "bool",
    "type", "True", "False", "None", "given",  # `_unfinished` is cell-local by its underscore
}


PLACEHOLDER_BODY = (ast.Pass,)


def _is_placeholder_def(node: ast.AST) -> bool:
    """A stub function: its body is just `...`, `pass` or `return None`."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    real = [st for st in node.body if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str))]
    if not real:
        return True
    return all(
        isinstance(st, PLACEHOLDER_BODY)
        or (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and st.value.value is Ellipsis)
        or (isinstance(st, ast.Return)
            and (st.value is None
                 or (isinstance(st.value, ast.Constant) and st.value.value is None)))
        for st in real
    )


def stub_call_results(source: str) -> set[str]:
    """Names assigned from a call to a not-yet-written function in the same cell.

    `def low_pass(...): ...` returns the sentinel, so `vfilt = low_pass(v, 5, dt)` is just as
    unfilled as a bare blank -- but nothing else spots it, and the plot below then received a
    sentinel it could not draw.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    stubs = {n.name for n in tree.body if _is_placeholder_def(n)}
    if not stubs:
        return set()
    names: set[str] = set()
    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or not isinstance(stmt.value, ast.Call):
            continue
        fn = stmt.value.func
        if isinstance(fn, ast.Name) and fn.id in stubs:
            for tgt in stmt.targets:
                names |= {
                    n.id for n in ast.walk(tgt)
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
                }
    return names


def undefined_toplevel(source: str, provided: set[str]) -> list[str]:
    """Names a stub reads at top level but never binds -- i.e. the blanks to be filled in.

    Bodies of functions and classes are skipped: a global referenced there only fails when the
    function is called, not when the cell runs.
    """
    import builtins

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    binds: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            binds.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            binds.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                binds.add(a.asname or a.name.split(".")[0])

    loads: set[str] = set()
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                loads.add(node.id)

    missing = loads - binds - provided - set(dir(builtins))
    return sorted(missing)


COMMENTED_ASSIGN_RE = re.compile(r"^\s*#\s*([A-Za-z_]\w*)\s*=(?!=)", re.M)


def commented_blanks(source: str) -> set[str]:
    """Blanks the book marks by commenting out the assignment (``# x = ....``).

    This is the source's own convention for "student fills this in", and it is a better signal
    than "name is undefined": exercise 4 wants its own `h`, but exercise 3 already bound `h=0.5`,
    so the name *is* defined and the stub would silently compute against the wrong value --
    `AttributeError: 'float' object has no attribute 'copy'`. Treating the commented assignment
    as a blank gives the cell its own placeholder, which the SSA pass then versions to `h_2`.
    """
    return set(COMMENTED_ASSIGN_RE.findall(source))


def self_assigned(source: str) -> set[str]:
    """Names the cell assigns a real value to at top level.

    A blank the cell then assigns for itself cannot gate anything. Root Finding 3.3 is the clear
    case: the book pre-allocates `sol6 = np.zeros(polyorder)` for the student to fill element by
    element, so `given(sol6)` was true on load, the guard opened, and the checker marked an array
    of zeros wrong before the reader had typed a character. ODE2 9.8 fails the other way --
    `t1 = find_tf(v1)` is assigned *inside* the guard, so `given(t1)` could never become true and
    the cell was dead whatever the reader did.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    out: set[str] = set()
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and not (
            isinstance(stmt.value, ast.Constant) and stmt.value.value is None
        ):
            out |= _bound_in(stmt)
    return out


def add_placeholders(source: str, provided: set[str]) -> tuple[str, tuple[str, ...], set[str]]:
    """Declare a stub's blanks as ``None``. Returns ``(source, blanks, defeated)``.

    Jupyter Book 1 never ran a cell until the student clicked it, so an unfilled stub was simply
    blank. marimo is reactive and runs everything on load, so the names have to exist.

    `defeated` are candidate blanks the cell assigns for itself (see `self_assigned`). They get
    no placeholder and no place in the guard -- but a cell left with *nothing* testable is
    unfinished all the same, and the caller falls back to the `_unfinished` switch.
    """
    candidates = (
        set(undefined_toplevel(source, provided))
        | commented_blanks(source)
        | stub_call_results(source)
    )
    defeated = candidates & self_assigned(source)
    missing = sorted(candidates - defeated)
    if not missing:
        return source, (), defeated
    head = [
        "# Fill these in as you work through the exercise.",
        " = ".join(missing) + " = None",
        "",
    ]
    return "\n".join([*head, source]), tuple(missing), defeated


def local_scopes(source: str, offset) -> list[tuple[int, int, set[str]]]:
    """Byte ranges of functions in this cell, with the names local to each.

    A parameter shadows a global, so renaming it is wrong: versioning turned
    `def update(zoom=1000)` into `def update(zoom_sol6=1000)` because an earlier solution
    happened to bind `zoom`.

    The exclusion has to be *scoped*, though. Removing the name from the mapping cell-wide also
    stops it being renamed at the call site, so `diff_forward(f, x, h)` silently picked up the
    student's empty stub `f` instead of the solution's own -- `NoneType - NoneType`.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    scopes: list[tuple[int, int, set[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if node.end_lineno is None:
            continue
        a = node.args
        names = {
            arg.arg
            for arg in [*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg]
            if arg is not None
        }
        body = node.body if isinstance(node.body, list) else [node.body]
        for stmt in body:
            names |= {
                n.id for n in ast.walk(stmt)
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
            }
        start = offset(node.lineno, node.col_offset)
        end = offset(node.end_lineno, node.end_col_offset)
        scopes.append((start, end, names))
    return scopes


def first_bindings(source: str, offset) -> dict[str, int]:
    """Offset of each name's first top-level binding in this cell.

    Cells execute top to bottom, so a read *before* the first binding still refers to the
    previous version of that name. ODE2's fourth solution does exactly this::

        sol = solve_ivp(dydt, (0, T), (x0, v0), t_eval=t)   # `t` from solution 1
        t = sol.t                                           # rebinds `t` here

    Renaming the whole cell uniformly produced `t_eval=t_sol4` one line before `t_sol4` existed.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    firsts: dict[str, int] = {}
    for stmt in tree.body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                pos = offset(node.lineno, node.col_offset)
                if node.id not in firsts or pos < firsts[node.id]:
                    firsts[node.id] = pos
    return firsts


def _retoken(source: str, mapping: dict[str, str], before: dict[str, str] | None = None) -> str:
    """Rename NAME tokens in place, preserving every other character exactly.

    ``tokenize.untokenize`` reflows whitespace -- it emits ``x =y =None`` and ``plt .plot (``,
    and re-indents comments -- which is unacceptable in code students read and edit. So the
    token stream is used only to locate the names, and the edits are spliced into the original
    text back-to-front.

    Attribute names (after a ``.``) and string literals are left alone; a commented-out
    assignment (``# h = ...``, the book's marker for a blank) is renamed too, so the hint and
    the code agree.
    """
    import io
    import tokenize

    try:
        toks = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return source

    lines = source.splitlines(keepends=True)
    offset = [0]
    for line in lines:
        offset.append(offset[-1] + len(line))

    def absolute(pos: tuple[int, int]) -> int:
        row, col = pos
        return offset[row - 1] + col

    at = lambda row, col: offset[row - 1] + col  # noqa: E731
    scopes = local_scopes(source, at)
    # reads before a name's first binding still refer to the previous version
    switch_at = first_bindings(source, at) if before else {}

    def shadowed(name: str, position: int) -> bool:
        return any(a <= position < b and name in names for a, b, names in scopes)

    def is_kwarg(index: int, depth: int) -> bool:
        """`f(vmax=vmax)` -- the left-hand `vmax` is a parameter name, not the variable.

        Renaming it produced `AxesImage.set() got an unexpected keyword argument 'vmax_sol8'`.
        The bracket depth matters: without it, tuple unpacking at statement level
        (`eigA, eigvA = ...`) looks identical and its second target stopped being renamed.
        """
        if depth <= 0:
            return False
        nxt = next(
            (t for t in toks[index + 1:] if t.type not in (tokenize.NL, tokenize.COMMENT)),
            None,
        )
        if nxt is None or nxt.string != "=":
            return False
        prv = next(
            (
                t
                for t in reversed(toks[:index])
                if t.type not in (tokenize.NL, tokenize.COMMENT, tokenize.INDENT)
            ),
            None,
        )
        return prv is not None and prv.string in {"(", ","}

    edits: list[tuple[int, int, str]] = []
    prev_dot = False
    depth = 0
    for position, tok in enumerate(toks):
        if tok.type == tokenize.OP:
            if tok.string in "([{":
                depth += 1
            elif tok.string in ")]}":
                depth -= 1
        if tok.type == tokenize.NAME and not prev_dot and not is_kwarg(position, depth):
            start = absolute(tok.start)
            new = mapping.get(tok.string)
            bind_at = switch_at.get(tok.string)
            if bind_at is not None and start < bind_at and before is not None:
                new = before.get(tok.string, tok.string)
            if new and new != tok.string and not shadowed(tok.string, start):
                edits.append((start, absolute(tok.end), new))
        elif tok.type == tokenize.COMMENT:
            cm = re.match(r"^#\s*([A-Za-z_]\w*)\s*=(?!=)", tok.string)
            if cm:
                new = mapping.get(cm.group(1))
                if new and new != cm.group(1):
                    start = absolute(tok.start) + cm.start(1)
                    edits.append((start, start + len(cm.group(1)), new))
        prev_dot = tok.type == tokenize.OP and tok.string == "."

    out = source
    for start, end, new in sorted(edits, reverse=True):
        out = out[:start] + new + out[end:]
    return out


NOTES: list[str] = []  # anything the plot converter could not do safely


def space_comments(source: str) -> str:
    """Put a blank line before a comment block that follows code, for legibility.

    Consecutive commented-out assignments (`# x = ...`) are one block and stay tight together --
    they are the list of blanks, and spacing them out would break them up.
    """
    lines = source.split("\n")
    out: list[str] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        is_comment = stripped.startswith("#")
        if is_comment and out:
            prev = out[-1].strip()
            prev_is_code = bool(prev) and not prev.startswith("#")
            # only break *into* a comment block, and never in the middle of a run of blanks
            if prev_is_code and not COMMENTED_ASSIGN_RE.match(line):
                out.append("")
        # the source is full of lines that are nothing but spaces; they read as stray indents
        out.append(line.rstrip() if not stripped else line)
    return "\n".join(out)


def transform_solution(source: str, sol_versions: dict[str, str], index: int) -> str:
    """Rule 1 (revised twice): solutions keep their own global chain, versioned per solution.

    The chapters are linear: solution 5 legitimately reads `t`, `t_fwd` and `fwd_derv` produced
    by solution 4. Wrapping each solution in a function would sever that chain and destroy the
    "I got stuck, let me just run the solutions" recovery path the original book relies on.

    A single flat ``_sol`` suffix is not enough either: several solutions rebind the same name
    (`x` is rebound by exercises 1 and 5), which marimo rejects with "x_sol was also defined by
    cell-19". So each binding gets its own version, ``<name>_sol<n>``, and reads resolve to the
    most recent version -- static single assignment, applied across cells.

    Students keep the natural names in their own stubs, so the two chains coexist inside
    marimo's one-definition-per-global rule.
    """
    src = strip_scaffold_comments(SENTINEL_RE.sub("", strip_imports(source)), solution=True)
    src, oo_notes, tail = to_object_oriented(src, wrap=False)
    NOTES.extend(f"solution {index}: {n}" for n in oo_notes)
    # underscore names are already cell-local; versioning them to `_ax_sol1` broke the
    # `show(_ax)` line that follows, which cannot see another cell's local anyway
    bound = {n for n in _bound(src) if n not in PROTECTED and not n.startswith("_")}

    counters = loop_only_names(src)
    mapping = dict(sol_versions)  # reads resolve to the latest version so far
    for name in sorted(counters):
        mapping[name] = f"_{name}"
    for name in bound - counters:  # this cell's bindings become a fresh version
        mapping[name] = f"{name}_sol{index}"

    # A solution that neither plots nor prints shows the reader nothing at all -- and the whole
    # point of leaving solutions executable was that their output is the teaching. Fall back to
    # displaying what it computed: `show(trapezoidal_integral=...)` renders "= 0.333", and for an
    # array, its shape. Built here, before renaming, so the keyword keeps the plain name while
    # the value picks up its `_sol<n>` suffix.
    reported: tuple[str, ...] = ()
    if tail is None and "print(" not in src:
        reported = answer_sources(src)
    if reported:
        src = src.rstrip() + "\n\n" + show_call(None, reported)

    src = _retoken(src, mapping, before=dict(sol_versions)).rstrip()
    for name in bound - counters:
        sol_versions[name] = f"{name}_sol{index}"
    src = space_comments(src)
    if reported:
        return src
    # Always, for the same reason as student cells: no output, no play button, no way to run it.
    src, tail = adopt_trailing_display(src, tail)
    return src.rstrip() + "\n\n" + show_call(tail, ())


def check_block(question: str, count: int) -> str:
    """One reactive check cell per exercise.

    Modelled on `mograder <https://jameskermode.github.io/mograder/>`_, whose student-facing
    ``check()`` returns an ``mo.callout`` rather than printing. That distinction matters here:
    marimo's built-in pytest integration *does* run inside an island, but its post-execution
    hook writes the report to ``sys.stdout``, which in an island lands in the browser console
    where no student will ever see it.

    The run button is gone. The check re-runs by itself whenever the answer changes, which is
    the instant feedback the exercise wants; premature checking is already prevented by the
    stub's own ``mo.stop``, since marimo will not run a stopped cell's descendants.
    """
    args = ", ".join(f"{question}_{i + 1}" for i in range(count))
    return (
        "```{marimo} python\n"
        ":editor: false\n\n"
        f'check_answers({args}, key="{question}")\n'
        "```"
    )


# --------------------------------------------------------------------------- page


# The not-filled-in-yet sentinel is plain `None`, written as `None` in the pages. It was briefly
# a named `UNSET` bound to a 2x2 NaN array, chosen so live scaffolding (`x[10]`, `len(x)`,
# `h.copy()`) would survive operating on an unfilled blank. It did not survive it meaningfully --
# `yt[10]` on a 2x2 raises `IndexError: index 10 is out of bounds for axis 0 with size 2`, which
# tells a reader nothing -- and it made `is_unanswered` guess at whether an all-NaN array was a
# sentinel or a real result. Statements that would trip over None are guarded explicitly instead
# (see `guard_unset`), and a second name for None was one concept more than the pages needed.
HEADER_IMPORTS = (
    "import numpy as np",
    "import marimo as mo",
    "import matplotlib.pyplot as plt",
)


def page_header(imports: list[str], setup: list[str], answers: dict) -> str:
    """The `{marimo-config}` block: imports, the answer bank, and the checker.

    All three go in `:header:`, which the plugin turns into a marimo *setup cell*. Setup cells
    execute in the browser but are dropped from the rendered output entirely -- no island, no
    empty box, nothing in the DOM. That is what the reader wants: the answer bank and the
    checker are machinery, not content, and a reader should never see either.

    They have to be written as a `---`-fenced YAML options block rather than as `:header: ...`
    one-liners. The one-line form does not parse block scalars: `:pyproject: |` passed the `|`
    through literally and TOML then choked on it. The fenced form is parsed as real YAML, so
    `header: |` works and the source can stay readable.
    """
    body = "\n\n".join(
        [
            "\n".join(HEADER_IMPORTS),
            *(i for i in imports if i not in HEADER_IMPORTS),
            *setup,
            f"ANSWERS = {python_literal(answers)}",
            CHECKER_SRC.strip(),
        ]
    )
    # A YAML block scalar takes its indentation from its first non-empty line; every non-empty
    # line has to clear it, and blank lines must stay truly blank.
    indented = "\n".join(f"  {ln}" if ln.strip() else "" for ln in body.split("\n"))
    return (
        "```{marimo-config}\n"
        "---\n"
        'pyproject: dependencies = ["numpy", "matplotlib", "scipy"]\n'
        "header: |\n"
        f"{indented}\n"
        "---\n"
        "```"
    )


def build_page(chapter: str) -> str:
    order, slug = CHAPTERS[chapter]
    blocks = parse_chapter(chapter_path(chapter))
    expanded = []
    for block in blocks:
        if block.kind != "code":
            expanded.append(block)
            continue
        block.source = apply_content_fixes(block.source, chapter)
        parts = split_for(block.source, chapter, block.is_solution)
        if parts is None:
            expanded.append(block)
            continue
        # one source cell becomes several; they stay one exercise/solution unit
        block.split = parts
        expanded.append(block)
    blocks = drop_cells(expanded, chapter)
    info = analyse(chapter)
    collide = set(info["scratch_collisions"])

    key_file = ANSWERS_DIR / f"{slug}.json"
    answers = json.loads(key_file.read_text()) if key_file.exists() else {}

    title = chapter.replace("_", " ").title().replace(" 1", " I").replace(" 2", " II")
    figure_names: dict[str, int] = {}

    out: list[str] = []
    out.append("---")
    out.append(f"title: {title}")
    out.append(f"label: {slug}_page")
    out.append("numbering:")
    out.append(f"  enumerator: {order}.%s")
    out.append("---")
    out.append("")
    # Every import in the chapter is hoisted here; marimo would otherwise see `np` bound by
    # many cells.
    imports = collect_imports(blocks)
    out.append(page_header(imports, collect_setup(blocks), answers))
    out.append("")

    i = 0
    ex_counter = 0
    open_exercise: str | None = None
    created_labels: set[str] = set()
    solved_labels: set[str] = set()
    sol_versions: dict[str, str] = {}
    sol_index = 0
    # globals already owned by an earlier cell on this page; a blank that is already defined
    # upstream must NOT get a placeholder, or the placeholder becomes a rival definition
    page_globals: set[str] = set()
    # Globals that exist but are still None: an earlier exercise's blanks, and anything a
    # guarded region would have computed from them. A chapter is a chain -- FT1 exercise 1
    # defines `t`, `y` and `fs`, and eight later cells are built on them -- so being unfilled
    # propagates forward, and every cell downstream has to guard against it too.
    unset_globals: set[str] = set()
    # function name -> the unfilled globals its body reads, so a later call is guarded too
    unset_fns: dict[str, set[str]] = {}
    stub_versions: dict[str, str] = {}
    stub_seen: dict[str, int] = {}
    provided = PROTECTED | imported_names(imports) | {"np", "mo", "plt"}

    while i < len(blocks):
        b = blocks[i]

        if b.kind == "code":
            if b.is_init or is_dropped(b.source, chapter):
                i += 1
                continue

            if b.is_check:
                q = QUESTION_RE.search(b.source)
                n = NUM_RE.search(b.source)
                if q:
                    count = int(n.group("n")) if n else 1
                    if open_exercise:
                        out.append(":::{exercise-end}\n:::\n")
                        open_exercise = None
                    out.append(check_block(q.group("q"), count))
                    out.append("")
                i += 1
                continue

            if b.is_solution:
                label = open_exercise or f"ex_{ANSWER_PREFIX.get(chapter, order)}_{ex_counter:02d}"
                if open_exercise:
                    out.append(":::{exercise-end}\n:::\n")
                    open_exercise = None
                # one `{solution}` per exercise: several exercises ship two solution cells,
                # and a second `{solution} ex_6_05` is a duplicate cross-reference
                gated = label in created_labels and label not in solved_labels
                if gated:
                    solved_labels.add(label)
                    out.append(f":::{{solution-start}} {label}\n:class: dropdown\n:::\n")
                else:
                    # a solution with no exercise of its own: `{solution}` would emit a dangling
                    # cross-reference ("target was not found: ex_6_05")
                    out.append("::::{admonition} Solution\n:class: dropdown\n")
                for part in (b.split or [b.source]):
                    sol_index += 1
                    out.append("```{marimo} python")
                    # :echo: shows the source; without it the dropdown opens on an output with
                    # no code, which is useless as a solution.
                    out.append(":echo: true")
                    out.append(":editor: false")
                    out.append("")
                    out.append(transform_solution(part, sol_versions, sol_index))
                    out.append("```")
                    out.append("")
                out.append(":::{solution-end}\n:::\n" if gated else "::::\n")
                i += 1
                continue

            # ordinary / stub cell
            for part in (b.split or [b.source]):
                if is_session_setup(part):
                    # hoisted into the page header by collect_setup(); nothing to render
                    continue
                src = strip_scaffold_comments(
                    SENTINEL_RE.sub("", strip_imports(part)), solution=False
                )
                if not src.strip():
                    continue
                src = normalise_stub(src)
                # placeholders first, while every read is still a top-level read
                src, blanks, defeated = add_placeholders(src, provided | page_globals)
                # A cell whose only blank is an array element (`#delta[i,j] = ...`) has nothing
                # to declare as None and nothing to test, so it gets the same visible switch as
                # a loop that cannot terminate. Without it PDE1 exercise 3 ran one pass over an
                # all-zero `delta`, exited, and handed the checker the initial condition as an
                # answer -- wrong, and confidently so.
                elem = unfinished_line(src, blanks, defeated)
                unfinished = has_unfinished_loop(src) or elem is not None
                # Blanks this cell owns, plus any still-None global it reads from an earlier
                # exercise. The second kind gets no placeholder -- the name belongs to another
                # cell, and a rival definition is exactly what marimo forbids -- but it has to
                # be guarded against and named in show() just the same.
                # A name this cell binds is its own, not an upstream dependency -- even though
                # the previous exercise used the same name for something else. Including it
                # made the guard test a variable the guard itself assigns, so it could never
                # become true and the cell stayed dark however much the student filled in.
                loaded, bound = _loaded(src), _bound_anywhere(src)
                need = unset_globals & loaded
                unsafe_calls = tuple(sorted(loaded & set(unset_fns)))
                for fn in unsafe_calls:
                    need |= unset_fns[fn] & unset_globals
                deps = tuple(sorted(need - set(blanks) - bound))
                waiting = blanks + deps + stub_fns(src)
                # Student cells stay flat; the tail is indented under an `if ... is not None`
                # only where a live statement would otherwise raise on an unfilled blank.
                src, oo_notes, tail = to_object_oriented(src, waiting, wrap=False)
                NOTES.extend(f"{slug} stub: {n}" for n in oo_notes)
                src, hoisted = guard_unset(
                    src, waiting, displayed=tail, triggers=unsafe_calls,
                    unfinished=unfinished, from_line=elem,
                )
                # Appended *before* renaming, so its blank names are versioned too -- otherwise
                # the call still said `dvdt=dvdt` after the variable became `dvdt_2`. Never
                # conditional: a cell that displays nothing has no play button, so it can never
                # be run, and 54 cells were reaching the page in exactly that state.
                src, tail = adopt_trailing_display(src, tail)
                src = src.rstrip() + "\n\n" + show_call(tail, waiting)
                # Anything bound outside the guard really is filled in, so a name reused here
                # for real work stops being "waiting"; the blanks and everything the guard
                # would have computed take its place.
                unset_globals -= _bound_outside_guard(src)
                unset_globals |= set(blanks) | {n for n in hoisted if not n.startswith("_")}
                unset_fns.update(functions_needing(src, unset_globals))
                src = transform_stub(src, stub_versions, stub_seen)
                src = space_comments(src)
                page_globals |= {n for n in _bound(src) if not n.startswith("_")}
                out.append("```{marimo} python")
                # Plain `:editor: true` is the only variant that renders an editable cell:
                # `:eval: false` hides it entirely and `:disabled:`/`:unparsable:` set
                # data-reactive="false" (see NOTES.md).
                out.append(":editor: true")
                out.append("")
                out.append(src)
                out.append("```")
                out.append("")
            i += 1
            continue

        # ---- markdown
        text = b.source
        if SOLUTION_RE.search(text):
            text = SOLUTION_RE.sub("", text).strip()
            if not text:
                i += 1
                continue

        text = apply_prose_fixes(text, chapter)
        for kind, segment in split_markdown(text):
            body = convert_markdown(segment.strip(), figure_names)
            if kind == "exercise":
                ex_counter += 1
                label = f"ex_{ANSWER_PREFIX.get(chapter, order)}_{ex_counter:02d}"
                if open_exercise:
                    out.append(":::{exercise-end}\n:::\n")
                created_labels.add(label)
                out.append(f":::{{exercise-start}}\n:label: {label}\n:::\n")
                out.append(body)
                out.append("")
                open_exercise = label
            elif kind == "selfcheck":
                # the self check belongs to the exercise that just ended
                if open_exercise:
                    out.append(":::{exercise-end}\n:::\n")
                    open_exercise = None
                fence = fence_for(body)
                out.append(f"{fence}{{tip}} Self check\n:class: dropdown\n")
                out.append(body)
                out.append(f"{fence}\n")
            else:
                if open_exercise:
                    out.append(":::{exercise-end}\n:::\n")
                    open_exercise = None
                out.append(body)
                out.append("")
        i += 1

    if open_exercise:
        out.append(":::{exercise-end}\n:::\n")

    return "\n".join(out).replace("\n\n\n\n", "\n\n") + "\n"


def _bound(src: str) -> set[str]:
    from dag_collisions import bound_names

    return bound_names(src)


CHECKER_SRC = '''
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
    return "\\n".join(lines)


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

    `print("N_iter %d\\r" % n, end="")` is a progress line: in a terminal each update overwrites
    the last, and the reader sees one line counting up. Concatenated into a buffer instead, PDE1's
    relaxation solution produced 65 KB of text in three newlines and 1909 carriage returns -- one
    unreadable line, and the single worst piece of output in the book. Keeping only what follows
    the last `\\r` of each line is what the author wrote the `\\r` to mean.
    """
    text = "".join(PRINTED)
    PRINTED.clear()
    return "\\n".join(last_write(line) for line in text.split("\\n"))


def last_write(line):
    # The final segment is usually empty -- the progress line ends with a carriage return and the
    # summary that follows begins with a newline -- so it is the last *non-empty* write that the
    # reader would have been left looking at.
    written = [seg for seg in line.split("\\r") if seg]
    return written[-1] if written else ""


# Long output is folded away rather than dumped: a solution that prints a row per iteration
# should not push the next exercise off the screen.
PRINT_HEAD, PRINT_TAIL = 12, 4


def format_printed(text):
    text = text.rstrip()
    lines = text.split("\\n")
    if len(lines) <= PRINT_HEAD + PRINT_TAIL + 1:
        return mo.md(f"```text\\n{text}\\n```")
    hidden = len(lines) - PRINT_HEAD - PRINT_TAIL
    shown = [*lines[:PRINT_HEAD], f"... {hidden} more lines ...", *lines[-PRINT_TAIL:]]
    return mo.vstack([
        mo.md("```text\\n" + "\\n".join(shown) + "\\n```"),
        mo.accordion({f"Show all {len(lines)} lines": mo.md(f"```text\\n{text}\\n```")}),
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
    that asks for a value read the same way at the call site.

    (A context manager would be the natural shape for "skip this block", but Python has no way to
    skip a `with` body without frame-tracing tricks, and those would be fragile inside marimo's
    own instrumented runtime. An `if` with a well-named condition costs one line and no magic.)
    """
    return all(written(v) if callable(v) else v is not None for v in values)


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
            mo.md(" \u00b7 ".join(f"`{k}` {describe(v)}" for k, v in blanks.items()))
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


def check_answers(*values, key):
    """Compare the student's answers against the stored reference values.

    Returns an mo.callout so the result renders in the cell, green/red/amber, in the style of
    mograder's student-facing check().
    """
    report, ok = [], True
    blanks = [f"{key}_{i}" for i, v in enumerate(values, start=1) if is_unanswered(v)]
    if len(blanks) == len(values):
        return mo.callout(
            mo.md("Waiting for your code: replace the `None` placeholders above."),
            kind="warn",
        )
    for i, value in enumerate(values, start=1):
        name = f"{key}_{i}"
        if is_unanswered(value):
            ok = False
            report.append(f"`{name}` has not been filled in yet.")
            continue
        if name not in ANSWERS:
            report.append(f"`{name}` has no stored answer, skipping.")
            continue
        sol, shape, stride = reference_answer(name)
        ans = np.asarray(value)
        if ans.shape != shape:
            ok = False
            report.append(f"`{name}` has the wrong shape: expected `{shape}`, got `{ans.shape}`.")
            continue
        if stride > 1:
            ans = ans[tuple(slice(None, None, stride) for _ in range(ans.ndim))]
        finite = sol[np.isfinite(sol)] if sol.size else sol
        atol = 1e-3 * np.max(np.abs(finite)) if finite.size else 1e-8
        atol = float(atol) or 1e-8
        if np.allclose(ans, sol, atol=atol, equal_nan=True):
            report.append(f"`{name}` is correct.")
        else:
            ok = False
            report.append(
                f"`{name}` has the right shape but incorrect values:\\n\\n"
                f"```\\n{diff_report(sol, ans, atol)}\\n```"
            )
    body = "\\n\\n".join(f"- {line}" if "\\n" not in line else line for line in report)
    if ok:
        return mo.callout(mo.md(f"**Correct.**\\n\\n{body}"), kind="success")
    return mo.callout(mo.md(f"**Not quite yet.**\\n\\n{body}"), kind="danger")
'''


def unparsable_cells(page: str) -> list[tuple[int, str]]:
    """Every emitted `{marimo}` cell must be valid Python. Report the ones that are not."""
    bad: list[tuple[int, str]] = []
    lines = page.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].strip() == "```{marimo} python":
            start = i + 1
            i += 1
            while i < len(lines) and lines[i].startswith(":"):
                i += 1
            body: list[str] = []
            while i < len(lines) and lines[i].strip() != "```":
                body.append(lines[i])
                i += 1
            try:
                ast.parse("\n".join(body))
            except SyntaxError as exc:
                bad.append((start + 1, f"{exc.msg} (cell line {exc.lineno})"))
        i += 1
    return bad


def header_locals(source: str) -> list[str]:
    """Underscore-prefixed names the header binds at top level -- all of them bugs.

    The header compiles to a marimo *setup cell*, and marimo makes an underscore-prefixed name
    local to the cell that defines it. Everything the header defines is shared machinery called
    from every other cell on the page, so a leading underscore is exactly wrong.

    It does not even fail consistently, which is what let it through: `PRINTED` was read directly
    inside a function body and resolved, while `last_write` was called from inside a *generator
    expression* -- a nested scope that marimo's cell-local rewriting does not reach -- and every
    cell on every page died with "Name `_last_write` is not defined".
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    out: set[str] = set()
    for stmt in tree.body:
        out |= _bound_in(stmt)
    return sorted(n for n in out if n.startswith("_"))


def header_source(page: str) -> str:
    """The Python inside the page's `header: |` block scalar."""
    lines = page.split("\n")
    try:
        start = next(i for i, ln in enumerate(lines) if ln.rstrip() == "header: |")
    except StopIteration:
        return ""
    body = []
    for ln in lines[start + 1:]:
        if ln.strip() and not ln.startswith("  "):
            break
        body.append(ln[2:] if ln.startswith("  ") else "")
    return "\n".join(body)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    if argv == ["--all"]:
        argv = [c for c, _ in sorted(CHAPTERS.items(), key=lambda kv: kv[1][0])]
    for chapter in argv:
        NOTES.clear()
        order, slug = CHAPTERS[chapter]
        page = build_page(chapter)
        out = ROOT / f"{order:02d}.{slug}.md"
        out.write_text(page, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}  ({len(page.splitlines())} lines)")
        # The header is a setup cell, not a `{marimo}` cell, so unparsable_cells() never sees
        # it -- and a broken header takes the whole page down at load.
        try:
            ast.parse(header_source(page))
        except SyntaxError as exc:
            print(f"    BROKEN HEADER: {exc.msg} (line {exc.lineno})")
        for name in header_locals(header_source(page)):
            print(f"    HEADER DEFINES A CELL-LOCAL: {name} (drop the leading underscore)")
        for lineno, err in unparsable_cells(page):
            # the inlined runtime is a Python string inside this file, so an escape that loses a
            # level silently emits broken source -- catch it here rather than in the browser
            print(f"    BROKEN CELL at page line {lineno}: {err}")
        for note in NOTES:
            print(f"    NEEDS REVIEW: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
