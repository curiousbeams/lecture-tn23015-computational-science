"""Report variables bound in more than one cell of a chapter.

marimo compiles every ``{marimo}`` cell on a page into one app, and forbids a global being
defined by more than one cell. This script finds every such collision so we know, before
converting, which names must become cell-local (underscore-prefixed in student stubs, or
function-scoped in solutions).

Solution cells (``hide-input``) are reported separately: under Rule 1 of the port they get
wrapped in ``def _solution()``, so their bindings never reach the global namespace and their
collisions are already solved.

Usage:
    .venv/bin/python scripts/dag_collisions.py [chapter_dir_name ...]
"""

from __future__ import annotations

import ast
import sys
from collections import defaultdict

from jb1_source import CHAPTERS, chapter_path, parse_chapter


def bound_names(source: str) -> set[str]:
    """Names a cell binds at cell scope.

    Loops and conditionals do *not* create a scope in Python, so a name assigned inside
    `while ...:` is every bit as global as one at the top level -- and marimo counts it. Scanning
    only `tree.body` missed exactly that: `integral` assigned inside a while loop was neither
    versioned nor reported as a collision, and marimo then refused to run the cell.

    Function and class bodies *do* create a scope, so they contribute only their own name.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    names: set[str] = set()

    def visit(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(child.name)
                continue  # its body has its own scope
            if isinstance(child, (ast.Lambda, ast.GeneratorExp, ast.ListComp,
                                  ast.SetComp, ast.DictComp)):
                continue
            if isinstance(child, ast.Assign):
                for tgt in child.targets:
                    names.update(_targets(tgt))
            elif isinstance(child, (ast.AugAssign, ast.AnnAssign)):
                names.update(_targets(child.target))
            elif isinstance(child, ast.For):
                names.update(_targets(child.target))
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                for alias in child.names:
                    names.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(child, ast.With):
                for item in child.items:
                    if item.optional_vars is not None:
                        names.update(_targets(item.optional_vars))
            visit(child)

    visit(tree)
    return names


def _targets(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        out: set[str] = set()
        for e in node.elts:
            out |= _targets(e)
        return out
    return set()


# Names that exist only inside the old check-answer boilerplate. Rule 3 of the port replaces
# that whole block with a single `check_answers(...)` call, so these collisions evaporate and
# should not be counted as work.
BOILERPLATE = {"question", "num", "to_check", "feedback", "passed", "var", "res", "msg"}


def analyse(chapter: str) -> dict:
    blocks = [b for b in parse_chapter(chapter_path(chapter)) if b.kind == "code"]

    student = defaultdict(list)   # name -> [cell idx]  (stubs + plain cells)
    solution = defaultdict(list)  # name -> [cell idx]  (hide-input cells)
    unparsable: list[int] = []

    for b in blocks:
        if b.is_init or b.is_check:
            # check cells are rewritten wholesale by Rule 3; their locals never survive
            continue
        try:
            ast.parse(b.source)
        except SyntaxError:
            unparsable.append(b.index)
        names = bound_names(b.source) - BOILERPLATE
        target = solution if b.is_solution else student
        for n in names:
            target[n].append(b.index)

    collisions = {n: idxs for n, idxs in student.items() if len(idxs) > 1}
    answer_collisions = {n: i for n, i in collisions.items() if n.startswith("answer_")}
    scratch_collisions = {n: i for n, i in collisions.items() if not n.startswith("answer_")}

    return {
        "chapter": chapter,
        "code_cells": len(blocks),
        "solution_cells": sum(1 for b in blocks if b.is_solution),
        "unparsable": unparsable,
        "scratch_collisions": scratch_collisions,
        "answer_collisions": answer_collisions,
        "globals_safe": sorted(n for n, i in student.items() if len(i) == 1),
    }


def main(argv: list[str]) -> int:
    chapters = argv or [c for c, _ in sorted(CHAPTERS.items(), key=lambda kv: kv[1][0])]
    total_scratch = 0
    print(f"{'chapter':36s} {'cells':>5s} {'sol':>4s} {'unparse':>7s} {'collide':>7s}")
    print("-" * 66)
    details = []
    for c in chapters:
        r = analyse(c)
        total_scratch += len(r["scratch_collisions"])
        print(
            f"{c:36s} {r['code_cells']:5d} {r['solution_cells']:4d} "
            f"{len(r['unparsable']):7d} {len(r['scratch_collisions']):7d}"
        )
        details.append(r)

    print(f"\nTotal scratch-name collisions to underscore: {total_scratch}\n")

    for r in details:
        if not r["scratch_collisions"] and not r["answer_collisions"]:
            continue
        print(f"### {r['chapter']}")
        for n, idxs in sorted(r["scratch_collisions"].items(), key=lambda kv: -len(kv[1])):
            print(f"    {n:24s} bound in {len(idxs):2d} cells {idxs}")
        for n, idxs in sorted(r["answer_collisions"].items()):
            print(f"    !! ANSWER {n:20s} bound in {len(idxs)} cells {idxs}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
