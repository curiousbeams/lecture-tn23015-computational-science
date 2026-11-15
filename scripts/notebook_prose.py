"""The chapter's explanation, for the notebooks: MyST prose turned into what marimo and Jupyter render.

    .venv/bin/python scripts/notebook_prose.py 03.root-finding.md            # preview, marimo
    .venv/bin/python scripts/notebook_prose.py 03.root-finding.md --jupyter  # preview, Jupyter

The notebooks a student opens (the badges, the two download zips) carry the whole chapter: every
paragraph, figure and admonition between the exercises, so nobody needs the book open beside
them. **The prose is still authored in one place, the chapter markdown.** It is copied into the
*generated* notebooks at build time and never written back. The ground-truth notebooks in
`marimo-notebooks/` stay as they are, with only the `head_*` questions, so `sync_cells.py` and
everything that edits those notebooks are untouched.

Two dialects, because the two runtimes render different markdown:

    marimo    pymdownx blocks, marimo's own syntax: `/// admonition | Title`, `/// details | Title`
    jupyter   CommonMark plus `<details>`: an admonition becomes a blockquote with a bold title

The Jupyter dialect is deliberately plain. `jupyterlab-myst` would render the MyST as-is, and it
would work in JupyterLite (it is a front-end extension, so it goes into the Lite *build*, not into
Pyodide). But the same notebooks are downloaded and opened in VS Code, PyCharm, Colab and plain
JupyterLab, where `:::{tip}` would show as literal text. The chapters use only a handful of
constructs, so converting them once here works everywhere.

Every construct the chapters use is handled explicitly, and anything else raises. A new directive
or cross-reference therefore stops the build instead of shipping as raw `:::{…}` text.

Figures load from the public repository on GitHub, as the exercise questions already did, so they
need an internet connection. The `{anywidget}` figures become code cells that run the same widget,
loading its module straight from its URL as the book does, through `tn23015.interactive_figure`:
hidden in marimo, a short `await interactive_figure(...)` in Jupyter.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_notebooks import FENCE, RAW, ROOT, exercise_numbers  # noqa: E402
from sync_cells import chapter_names  # noqa: E402

BOOK_URL = "https://cbl.curve.space/articles/curious-beams-lecture-tn23015-computational-science"
WIKI = "https://en.wikipedia.org/wiki/"

# The badge block points *at* the notebooks, so inside one it is noise.
NOTEBOOK_BADGE = "Rather work in a notebook?"

ADMONITIONS = {"note", "tip", "hint", "important", "warning", "seealso", "attention", "caution",
               "danger", "error"}
TITLES = {"seealso": "See also"}

OPEN = re.compile(r"^(:{3,})\{([a-z-]+)\}\s*(.*?)\s*$")
OPTION = re.compile(r"^:([a-z-]+):\s*(.*?)\s*$")
CODE_FENCE = re.compile(r"^\s*(`{3,}|~{3,})[^`]*$")
HEADING = re.compile(r"^#{1,6} ")


@dataclass
class Directive:
    name: str
    arg: str
    options: dict[str, str]
    body: list[str]
    colons: int


@dataclass
class Code:
    """A fenced code block in the prose: copied verbatim, never split or converted."""
    lines: list[str]


@dataclass
class Widget:
    """An `{anywidget}`: its own cell, because in marimo it is code, not markdown."""
    module: str
    model: dict


@dataclass
class Context:
    dialect: str                # "marimo" | "jupyter"
    page: Path
    numbers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.numbers = all_exercise_numbers()


# --------------------------------------------------------------------------------------------
# reading the page

def body(text: str) -> list[str]:
    """The page below its front matter, without the `{marimo-config}` header."""
    lines = text.split("\n")
    i = lines.index("---", 1) + 1 if lines and lines[0].strip() == "---" else 0
    out = []
    while i < len(lines):
        if lines[i].startswith("```{marimo-config}"):
            i += 1
            while lines[i].rstrip() != "```":
                i += 1
        else:
            out.append(lines[i])
        i += 1
    return out


def walk(text: str):
    """("prose", lines) and ("cell", name) in page order, the names being the notebooks' own.

    Code blocks are found exactly as `extract_notebooks.cells` finds them, and named by the same
    rule (`sync_cells.chapter_names`). The assertion at the end makes sure the two walks agree, so
    prose can never end up attached to the wrong cell.
    """
    names = iter(chapter_names(text))
    lines, prose, i = body(text), [], 0
    while i < len(lines):
        if lines[i].strip() == FENCE:
            yield "prose", prose
            prose = []
            i += 1
            while lines[i].strip() != "```":
                i += 1
            yield "cell", next(names)
        else:
            prose.append(lines[i])
        i += 1
    yield "prose", prose
    left = next(names, None)
    assert left is None, f"the prose walk missed the cell {left}"


def parse(lines: list[str]) -> list:
    """Lines -> a flat list of text lines, `Code` blocks and `Directive`s (bodies left unparsed)."""
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        fence = CODE_FENCE.match(line)
        if fence and "{" not in line:
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(fence.group(1)):
                j += 1
            out.append(Code(lines[i:j + 1]))
            i = j + 1
            continue
        m = OPEN.match(line)
        if m:
            colons, name, arg = m.groups()
            j, options = i + 1, {}
            while j < len(lines) and OPTION.match(lines[j]):
                key, value = OPTION.match(lines[j]).groups()
                options[key] = value
                j += 1
            k = j
            while k < len(lines) and lines[k].rstrip() != colons:
                k += 1
            if k == len(lines):
                raise ValueError(f"unclosed {{{name}}} directive: {line!r}")
            out.append(Directive(name, arg, options, lines[j:k], len(colons)))
            i = k + 1
            continue
        out.append(line)
        i += 1
    return out


# --------------------------------------------------------------------------------------------
# cross-references and links

def all_exercise_numbers() -> dict[str, str]:
    """{exercise key: its number}, across every chapter, since a reference can cross chapters."""
    out = {}
    for page in sorted(ROOT.glob("[01][0-9].*.md")):
        out |= exercise_numbers(page.read_text(encoding="utf-8"))
    return out


def page_slug(page: Path) -> str:
    """The page's path on the book site: `03.root-finding` -> `root-finding`, as mystmd does."""
    return re.sub(r"^\d+", "", page.stem).lstrip(".-_").replace(".", "-")


def page_links() -> dict[str, tuple[str, str]]:
    """{page label: (title, url)}, for `[](#root-finding_page)`."""
    out = {}
    for page in sorted(ROOT.glob("[01][0-9]*.md")):
        text = page.read_text(encoding="utf-8")
        label = re.search(r"^label:\s*(\S+)\s*$", text, re.M)
        title = re.search(r"^title:\s*(.+?)\s*$", text, re.M)
        if label and title:
            out[label.group(1)] = (title.group(1), f"{BOOK_URL}/{page_slug(page)}")
    return out


PAGES = page_links()


def inline(line: str, ctx: Context) -> str:
    def exercise(m):
        return m.group(1) or f"Exercise {ctx.numbers[m.group(2)]}"

    def page(m):
        title, url = PAGES[m.group(2)]
        return f"[{m.group(1) or title}]({url})"

    def wiki(m):
        return f"[{m.group(1) or unquote(m.group(2)).replace('_', ' ')}]({WIKI}{m.group(2)})"

    line = re.sub(r"\[([^\]]*)\]\(#ex_([0-9a-z_]+)\)", exercise, line)
    line = re.sub(r"\[([^\]]*)\]\(#([A-Za-z0-9_-]+_page)\)", page, line)
    line = re.sub(r"\[([^\]]*)\]\(wiki:([^)\s]+)\)", wiki, line)
    left = re.search(r"\]\(#[^)]*\)|\]\(wiki:|\{[a-z-]+\}`", line)
    if left:
        raise ValueError(f"{ctx.page.name}: no notebook rendering for {left.group(0)!r} in {line!r}")
    return line


# --------------------------------------------------------------------------------------------
# rendering

def render(nodes: list, ctx: Context) -> list[str]:
    out = []
    for node in nodes:
        if isinstance(node, str):
            out.append(inline(node, ctx))
        elif isinstance(node, Code):
            out.extend(node.lines)
        else:
            out.extend(directive(node, ctx))
    return out


def directive(node: Directive, ctx: Context) -> list[str]:
    name = node.name
    if name == "exercise-start":
        return [f"### Exercise {ctx.numbers[node.options['label'][3:]]}"]
    if name == "exercise-end":
        return []
    if name == "figure":
        return [figure(node)]
    if name == "admonition" or name in ADMONITIONS:
        title = node.arg or TITLES.get(name, name.title())
        if name == "admonition" and title == NOTEBOOK_BADGE:
            return []
        classes = node.options.get("class", "").split()
        kind = name if name != "admonition" else next(
            (c for c in classes if c in ADMONITIONS), "note")
        inner = trim(render(parse(node.body), ctx))
        return box(kind, title, inner, "dropdown" in classes, node.colons, ctx.dialect)
    raise ValueError(f"{ctx.page.name}: no notebook rendering for the {{{name}}} directive")


def figure(node: Directive) -> str:
    src = RAW + node.arg.removeprefix("./")
    alt = " ".join(ln.strip() for ln in node.body).strip()
    width = node.options.get("width")
    if width and width != "100%":
        return f'<img src="{src}" alt="{alt}" width="{width}">'
    return f"![{alt}]({src})"


def box(kind: str, title: str, inner: list[str], fold: bool, colons: int, dialect: str) -> list[str]:
    if dialect == "marimo":
        # One slash per MyST colon, so nesting carries over exactly: pymdownx, like MyST, closes a
        # block only at a fence of its own length.
        fence = "/" * colons
        head = f"{fence} {'details' if fold else 'admonition'} | {title}"
        return [head, f"    type: {kind}", "", *inner, fence]
    if fold:
        return ["<details>", f"<summary><strong>{title}</strong></summary>", "", *inner, "",
                "</details>"]
    return [f"> **{title}**", ">", *[f"> {ln}" if ln.strip() else ">" for ln in inner]]


def trim(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


# --------------------------------------------------------------------------------------------
# splitting into cells

def parts(lines: list[str], ctx: Context) -> list:
    """A prose chunk -> markdown strings and `Widget`s, one per notebook cell.

    A new cell starts at every heading and every exercise, so a section and an exercise question
    each get their own cell. That keeps the question directly above the cell it is about.
    """
    out, current = [], []

    def flush():
        text = re.sub(r"\n\s*\n(\s*\n)+", "\n\n", "\n".join(trim(render(current, ctx))))
        if text.strip():
            out.append(text)
        current.clear()

    for node in parse(lines):
        if isinstance(node, str) and HEADING.match(node):
            flush()
        elif isinstance(node, Directive) and node.name == "exercise-start":
            flush()
        elif isinstance(node, Directive) and node.name == "anywidget":
            flush()
            out.append(Widget(node.arg, json5(node.body)))
            continue
        current.append(node)
    flush()
    return out


def json5(lines: list[str]) -> dict:
    """The widget's model. MyST reads it as JSON5; these are JSON5 only in the unquoted keys and
    the trailing comma, so those are all this undoes."""
    text = "\n".join(lines)
    text = re.sub(r"^(\s*)([A-Za-z_]\w*)\s*:", r'\1"\2":', text, flags=re.M)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


def prose(page: Path, dialect: str) -> tuple[dict[str, list], list]:
    """({cell name: the prose cells that go before it}, the prose cells after the last one).

    The first entry opens with the chapter's `# Title`, in a cell of its own.
    """
    text = page.read_text(encoding="utf-8")
    ctx = Context(dialect, page)
    title = re.search(r"^title:\s*(.+?)\s*$", text, re.M).group(1)
    before, pending = {}, [f"# {title}"]
    for kind, item in walk(text):
        if kind == "prose":
            pending += parts(item, ctx)
        else:
            if pending:
                before[item] = pending
            pending = []
    return before, pending


# --------------------------------------------------------------------------------------------
# the two cell formats

def marimo_markdown(text: str) -> str:
    """A hidden marimo cell showing `text`, in the layout `marimo edit` (0.24) itself writes."""
    assert '"""' not in text, "the prose contains a triple quote"
    body = "\n".join(("    " + ln.rstrip()) if ln.strip() else "" for ln in text.split("\n"))
    return f'@app.cell(hide_code=True)\ndef _():\n    mo.md(r"""\n{body}\n    """)\n    return\n'


def marimo_widget(widget: Widget) -> str:
    """A hidden marimo cell drawing the `{anywidget}` with `tn23015.interactive_figure`.

    That is a coroutine because in the browser it installs anywidget on first use, so the cell is
    `async`. The import is underscored so that it stays local to the cell: a chapter may have more
    than one figure, and marimo allows each global name in one cell only.
    """
    return "\n".join([
        "@app.cell(hide_code=True)",
        "async def _():",
        "    # An interactive figure from the book. It loads from the internet.",
        "    from tn23015 import interactive_figure as _interactive_figure",
        "",
        *("    " + ln for ln in figure_call(widget, "_interactive_figure")),
        "    return",
        "",
    ])


def jupyter_widget(widget: Widget) -> str:
    """A code cell drawing the `{anywidget}` with `tn23015.interactive_figure`, as in marimo.

    JupyterLite has the widget extensions in its build (`build_jupyter_lite.sh`), and the function
    installs the Python package in the browser. IPython runs a top-level `await` in any kernel.
    """
    return "\n".join([
        "# An interactive figure from the book: run this cell to draw it. It loads from the internet.",
        "from tn23015 import interactive_figure",
        "",
        *figure_call(widget, "interactive_figure"),
    ])


# `interactive_figure`'s default module, so a call names the module only when it is another one
FIGURE_MODULE = re.search(r'^FIGURE_MODULE = "(.+)"$',
                          (ROOT / "packages" / "tn23015.py").read_text(), re.M).group(1)


def figure_call(widget: Widget, name: str) -> list[str]:
    """`await <name>(notebook, cells=[...], ...)`, one argument a line, with the directive's
    JSON body as its arguments.

    The figure follows the notebook's light or dark theme, but an editor it cannot read would
    leave it clashing with the page, so the fix is in every call, commented out, for the student
    to find where they are looking.
    """
    def literal(value):
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, list):
            return "[" + ", ".join(map(literal, value)) + "]"
        if isinstance(value, dict):
            return "{" + ", ".join(f"{literal(k)}: {literal(v)}" for k, v in value.items()) + "}"
        return repr(value)

    model = dict(widget.model)
    args = [literal(model.pop("notebook"))] + [f"{k}={literal(v)}" for k, v in model.items()]
    if widget.module != FIGURE_MODULE:
        args.append(f"module={literal(widget.module)}")
    if "theme" not in widget.model:
        args.append('# theme="dark",  # if the colours look wrong, uncomment this (or use "light")')
    return [f"await {name}(", *(f"    {a}" + ("" if a.startswith("#") else ",") for a in args), ")"]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.split("\n\n")[1])
        return 2
    page = ROOT / argv[0]
    dialect = "jupyter" if "--jupyter" in argv else "marimo"
    before, tail = prose(page, dialect)
    for name, cells in [*before.items(), ("(end)", tail)]:
        for cell in cells:
            if isinstance(cell, Widget):
                cell = marimo_widget(cell) if dialect == "marimo" else jupyter_widget(cell)
            print(f"----- before {name}\n{cell}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
