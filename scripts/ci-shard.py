#!/usr/bin/env python3
"""Rewrite _quarto.yml's project.render list to one shard's slice of the site.

Used by CI to render the site in parallel matrix jobs. Stdlib only. The
render: block is spliced by regex so the rest of _quarto.yml (comments,
formatting) is untouched. Deterministic: every job computes the same
partition. --count 1 writes the full explicit file list (escape hatch).
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUARTO_YML = ROOT / "_quarto.yml"

RENDER_BLOCK_RE = re.compile(r"^  render:\n((?:    (?:-|#)[^\n]*\n)+)", re.M)


def render_entries(text):
    m = RENDER_BLOCK_RE.search(text)
    if m is None:
        sys.exit("ci-shard: could not locate the render: block in _quarto.yml")
    entries = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            entries.append(line[2:].strip().strip('"').strip("'"))
    return m, entries


def is_rendered(rel_parts):
    # Quarto skips files/dirs starting with "_" or "."
    return not any(p.startswith(("_", ".")) for p in rel_parts)


def expand(entries):
    files, seen = [], set()

    def add(path):
        rel = path.relative_to(ROOT).as_posix()
        if rel not in seen:
            seen.add(rel)
            files.append(rel)

    for entry in entries:
        entry = entry.lstrip("/")
        path = ROOT / entry
        if "*" in entry:
            for f in sorted(ROOT.glob(entry)):
                if f.suffix == ".qmd" and is_rendered(f.relative_to(ROOT).parts):
                    add(f)
        elif entry.endswith(".qmd"):
            if path.exists():
                add(path)
        elif path.is_dir():
            for f in sorted(path.rglob("*.qmd")):
                if is_rendered(f.relative_to(ROOT).parts):
                    add(f)
    return files


def weight(rel):
    try:
        text = (ROOT / rel).read_text(errors="ignore")
    except OSError:
        return 1
    if "{shinylive-python}" in text or "{shinylive-r}" in text or "```{python}" in text:
        return 4
    return 1


def partition(files, count):
    weights = {f: weight(f) for f in files}
    buckets = [[] for _ in range(count)]
    loads = [0] * count
    for f in sorted(files, key=lambda p: (-weights[p], p)):
        i = loads.index(min(loads))
        buckets[i].append(f)
        loads[i] += weights[f]
    for b in buckets:
        b.sort()
        if "index.qmd" in b:
            b.remove("index.qmd")
            b.insert(0, "index.qmd")
    return buckets, loads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, required=True, help="1-based shard index")
    ap.add_argument("--count", type=int, required=True, help="total shards")
    args = ap.parse_args()
    if not (1 <= args.shard <= args.count):
        sys.exit(f"ci-shard: --shard must be in 1..{args.count}")

    text = QUARTO_YML.read_text()
    m, entries = render_entries(text)
    files = expand(entries)
    if not files:
        sys.exit("ci-shard: render list expanded to zero files")
    buckets, loads = partition(files, args.count)
    mine = buckets[args.shard - 1]
    if not mine:
        sys.exit(f"ci-shard: shard {args.shard}/{args.count} is empty")

    block = "  render:\n" + "".join(f"    - {f}\n" for f in mine)
    QUARTO_YML.write_text(text[: m.start()] + block + text[m.end():])
    print(f"shard {args.shard}/{args.count}: {len(mine)} files, weight {loads[args.shard - 1]}")


if __name__ == "__main__":
    main()
