"""Rebuild per-chapter answer keys: drop cross-pollution, drop stale duplicates, downsample.

The original ``values.json`` files total 121 MB and are shipped verbatim to every student's
browser. They are also polluted: ``hdf5_to_json.py`` never reset its accumulator between files,
so e.g. ``Ordinary_differential_equations_1/values.json`` carries ``answer_12_*`` keys belonging
to the next chapter, and ``Numerical_differentiation`` holds both ``answer_3_01_1`` and
``answer_3_1_1`` from an old renaming.

This script keeps only the keys a chapter's own check cells actually ask for, and stores large
arrays in a downsampled form that still catches shape and value errors:

    {"__downsampled__": true, "shape": [2001, 2001], "stride": 21, "values": [...]}

Complex answers keep the original ``{"real": [...], "imag": [...]}`` split, since JSON has no
complex type.

Usage:
    .venv/bin/python scripts/rebuild_answers.py [chapter_dir_name ...]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

from jb1_source import CHAPTERS, SRC_ROOT, chapter_path, parse_chapter

OUT_DIR = Path(__file__).resolve().parent.parent / "answers"

# Keep arrays up to this many elements verbatim; downsample anything larger to <= TARGET.
FULL_LIMIT = 4_000
TARGET = 2_500

QUESTION_RE = re.compile(r'question\s*=\s*["\'](?P<q>answer_[0-9a-zA-Z_]+)["\']')
NUM_RE = re.compile(r"num\s*=\s*(?P<n>\d+)")
ASSIGN_RE = re.compile(r"^\s*(?P<name>answer_[0-9a-zA-Z_]+)\s*=", re.M)


def required_keys(chapter: str) -> set[str]:
    """Keys this chapter's own cells reference: from check cells and from assignments."""
    keys: set[str] = set()
    for b in parse_chapter(chapter_path(chapter)):
        if b.kind != "code":
            continue
        q = QUESTION_RE.search(b.source)
        n = NUM_RE.search(b.source)
        if q and n:
            keys.update(f"{q.group('q')}_{i + 1}" for i in range(int(n.group("n"))))
        elif q:
            keys.add(q.group("q"))
        keys.update(ASSIGN_RE.findall(b.source))
    return keys


def source_json(chapter: str) -> Path | None:
    d = SRC_ROOT / chapter
    for candidate in ("values.json", "values_part_1.json"):
        p = d / candidate
        if p.exists():
            return p
    return None


def _as_array(value):
    """Return (array, is_complex) for a stored value, or (None, False) if not numeric."""
    if isinstance(value, dict) and "real" in value and "imag" in value:
        return np.array(value["real"]) + 1j * np.array(value["imag"]), True
    try:
        arr = np.array(value, dtype=float)
    except (ValueError, TypeError):
        return None, False
    return arr, False


def _encode(arr: np.ndarray, is_complex: bool):
    def pack(a: np.ndarray):
        if is_complex:
            return {"real": np.real(a).tolist(), "imag": np.imag(a).tolist()}
        return a.tolist()

    if arr.size <= FULL_LIMIT:
        return pack(arr)

    # Stride each axis so the kept sample lands near TARGET elements.
    ndim = max(arr.ndim, 1)
    factor = (arr.size / TARGET) ** (1.0 / ndim)
    stride = max(2, int(np.ceil(factor)))
    sl = tuple(slice(None, None, stride) for _ in range(arr.ndim))
    sample = arr[sl]
    return {
        "__downsampled__": True,
        "shape": list(arr.shape),
        "stride": stride,
        "values": pack(sample),
    }


def rebuild(chapter: str) -> dict:
    src = source_json(chapter)
    if src is None:
        return {"chapter": chapter, "error": "no values json"}

    wanted = required_keys(chapter)
    raw = json.loads(src.read_text())

    kept: dict[str, object] = {}
    downsampled = 0
    missing = []
    for key in sorted(wanted):
        if key not in raw:
            missing.append(key)
            continue
        arr, is_cx = _as_array(raw[key])
        if arr is None:
            kept[key] = raw[key]
            continue
        enc = _encode(arr, is_cx)
        if isinstance(enc, dict) and enc.get("__downsampled__"):
            downsampled += 1
        kept[key] = enc

    slug = CHAPTERS[chapter][1]
    out = OUT_DIR / f"{slug}.json"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(kept, separators=(",", ":")))

    return {
        "chapter": chapter,
        "src_mb": src.stat().st_size / 1e6,
        "out_mb": out.stat().st_size / 1e6,
        "src_keys": len(raw),
        "kept_keys": len(kept),
        "dropped": len(raw) - len(kept),
        "downsampled": downsampled,
        "missing": missing,
    }


def main(argv: list[str]) -> int:
    chapters = argv or [c for c, _ in sorted(CHAPTERS.items(), key=lambda kv: kv[1][0])]
    tot_src = tot_out = 0.0
    print(f"{'chapter':36s} {'src MB':>8s} {'out MB':>8s} {'keys':>10s} {'drop':>5s} {'dsmp':>5s}")
    print("-" * 78)
    allmissing = {}
    for c in chapters:
        r = rebuild(c)
        if "error" in r:
            print(f"{c:36s}  {r['error']}")
            continue
        tot_src += r["src_mb"]
        tot_out += r["out_mb"]
        print(
            f"{c:36s} {r['src_mb']:8.2f} {r['out_mb']:8.2f} "
            f"{r['kept_keys']:4d}/{r['src_keys']:<5d} {r['dropped']:5d} {r['downsampled']:5d}"
        )
        if r["missing"]:
            allmissing[c] = r["missing"]
    print("-" * 78)
    print(f"{'TOTAL':36s} {tot_src:8.2f} {tot_out:8.2f}")

    if allmissing:
        print("\nKeys referenced by cells but absent from the source JSON:")
        for c, keys in allmissing.items():
            print(f"  {c}: {', '.join(keys)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
