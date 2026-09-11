"""Shared parser for the original TeachBooks jupytext ``.md`` chapters.

The source book pairs every ``.ipynb`` with a byte-identical jupytext ``.md`` written in the
plain *markdown* flavour (not MyST): cells are fenced as ``` ```python ``` and tagged cells as
``` ```python tags=["hide-input"] ```. This module turns one of those files into an ordered list
of blocks so the other scripts can work on structure rather than regexes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

SRC_ROOT = Path(
    "/Users/gvarnavides/Documents/myst-sites/"
    "Computational-Science-Interactive-Textbook/book/content"
)

# Chapter directory -> (order, slug). Order follows _toc.yml.
CHAPTERS: dict[str, tuple[int, str]] = {
    "Numerical_differentiation": (1, "numerical-differentiation"),
    "Numerical_integration": (2, "numerical-integration"),
    "Root_finding": (3, "root-finding"),
    "Linear_algebra": (4, "linear-algebra"),
    "Fourier_transforms_1": (5, "fourier-transforms-1"),
    "Fourier_transforms_2": (6, "fourier-transforms-2"),
    "Random_numbers": (7, "random-numbers"),
    "Ordinary_differential_equations_1": (8, "ordinary-differential-equations-1"),
    "Ordinary_differential_equations_2": (9, "ordinary-differential-equations-2"),
    "Partial_differential_equations_1": (10, "partial-differential-equations-1"),
    "Partial_differential_equations_2": (11, "partial-differential-equations-2"),
}

# The "lecture number" used in that chapter's answer keys (answer_<n>_<ex>_<i>).
ANSWER_PREFIX: dict[str, int] = {
    "Numerical_differentiation": 3,
    "Numerical_integration": 4,
    "Root_finding": 5,
    "Linear_algebra": 6,
    "Fourier_transforms_1": 7,
    "Fourier_transforms_2": 8,
    "Random_numbers": 9,
    "Ordinary_differential_equations_1": 11,
    "Ordinary_differential_equations_2": 12,
    "Partial_differential_equations_1": 13,
    "Partial_differential_equations_2": 14,
}

FENCE_RE = re.compile(r"^(?P<fence>```+)\s*(?P<info>.*)$")
TAGS_RE = re.compile(r'tags=\[(?P<tags>[^\]]*)\]')


@dataclass
class Block:
    """One markdown or code block from the source chapter."""

    kind: str  # "markdown" | "code"
    source: str
    tags: list[str] = field(default_factory=list)
    index: int = -1
    # a single source cell that the converter expands into several (see SPLIT_CELLS)
    split: list[str] | None = None

    @property
    def is_solution(self) -> bool:
        return "hide-input" in self.tags

    @property
    def is_init(self) -> bool:
        return "thebe-init" in self.tags or "auto-execute-page" in self.tags

    @property
    def is_check(self) -> bool:
        return "check_answer" in self.source and "to_check" in self.source


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    return text[end + 4 :] if end != -1 else text


def parse_chapter(path: Path) -> list[Block]:
    """Split a jupytext markdown file into ordered markdown/code blocks."""
    text = strip_frontmatter(path.read_text(encoding="utf-8"))
    # jupytext region markers carry no meaning for us
    text = text.replace("<!-- #region -->", "").replace("<!-- #endregion -->", "")

    blocks: list[Block] = []
    buf: list[str] = []
    lines = text.split("\n")
    i = 0

    def flush_markdown() -> None:
        body = "\n".join(buf).strip("\n")
        if body.strip():
            blocks.append(Block("markdown", body))
        buf.clear()

    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        # only treat as a cell if the info string starts a python cell
        if m and m.group("info").strip().startswith("python"):
            fence = m.group("fence")
            info = m.group("info")
            tags: list[str] = []
            tm = TAGS_RE.search(info)
            if tm:
                tags = [t.strip().strip("\"'") for t in tm.group("tags").split(",") if t.strip()]
            i += 1
            body: list[str] = []
            while i < len(lines) and not lines[i].startswith(fence):
                body.append(lines[i])
                i += 1
            i += 1  # closing fence
            flush_markdown()
            blocks.append(Block("code", "\n".join(body).strip("\n"), tags))
        else:
            buf.append(lines[i])
            i += 1
    flush_markdown()

    for n, b in enumerate(blocks):
        b.index = n
    return blocks


def chapter_path(name: str) -> Path:
    return SRC_ROOT / name / f"{name}.md"


def iter_chapters():
    for name, (order, slug) in sorted(CHAPTERS.items(), key=lambda kv: kv[1][0]):
        yield name, order, slug, chapter_path(name)
