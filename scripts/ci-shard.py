#!/usr/bin/env python3
"""Rewrite _quarto.yml's project.render list to one shard's slice of the site.

Used by CI to render the site in parallel matrix jobs. Stdlib only. The
render: block is spliced by regex so the rest of _quarto.yml (comments,
formatting) is untouched. Deterministic: every job computes the same
partition. --count 1 is a pure full render: nothing is modified.

Besides the render list, sidebar configs are transformed: Quarto prunes
sidebar entries given as bare .qmd paths when the target is not in the
render list, so every bare qmd sidebar entry (in the metadata-files
sidebars and in _quarto.yml's website.sidebar) is converted to an
explicit {text, href} pair, which Quarto keeps. The text comes from the
page's front-matter title, else its first H1 heading, else the file stem.
All shards apply the identical transform; only the render list differs.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUARTO_YML = ROOT / "_quarto.yml"

RENDER_BLOCK_RE = re.compile(r"^  render:\n((?:    (?:-|#)[^\n]*\n)+)", re.M)
METADATA_FILES_RE = re.compile(r"^metadata-files:\n((?:  - [^\n]*\n)+)", re.M)
BARE_QMD_ITEM_RE = re.compile(r"^(\s*)- ((?:[\w.\-]+/)*[\w.\-]+\.qmd)\s*$", re.M)
FRONT_MATTER_TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.M)
H1_RE = re.compile(r"^#\s+(.+?)\s*(?:\{[^{}]*\})?\s*$", re.M)


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


def front_matter(rel):
    try:
        text = (ROOT / rel).read_text(errors="ignore")
    except OSError:
        return ""
    body = text.lstrip("﻿ \t\r\n")
    if not body.startswith("---"):
        return ""
    end = body.find("\n---", 3)
    return body[3:end] if end != -1 else ""


LISTING_PATTERN_RE = re.compile(
    r"^\s*(?:-|contents:)\s*([\w*.\-/]+\.qmd)\s*$", re.M
)


def listing_groups(files):
    """Groups of files that must render in the same shard.

    Quarto listing pages only include documents present in the render
    list, so a page whose listing contents glob project qmds must be
    co-sharded with every file its globs match.
    """
    fileset = set(files)
    groups = []
    for rel in files:
        fm = front_matter(rel)
        if "listing" not in fm:
            continue
        base = Path(rel).parent
        members = {rel}
        for m in LISTING_PATTERN_RE.finditer(fm):
            pat = m.group(1)
            matches = [
                p.relative_to(ROOT).as_posix()
                for p in sorted((ROOT / base).glob(pat))
            ]
            if not matches:  # fall back to project-root-relative patterns
                matches = [
                    p.relative_to(ROOT).as_posix()
                    for p in sorted(ROOT.glob(pat.lstrip("/")))
                ]
            members.update(f for f in matches if f in fileset)
        if len(members) > 1:
            groups.append(members)
    # merge overlapping groups
    merged = []
    for g in groups:
        for mg in merged:
            if mg & g:
                mg |= g
                break
        else:
            merged.append(set(g))
    return merged


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
    grouped = set()
    items = []  # (member list, total weight)
    for g in listing_groups(files):
        members = sorted(g)
        items.append((members, sum(weights[f] for f in members)))
        grouped |= g
    items.extend(([f], weights[f]) for f in files if f not in grouped)
    buckets = [[] for _ in range(count)]
    loads = [0] * count
    for members, w in sorted(items, key=lambda it: (-it[1], it[0][0])):
        i = loads.index(min(loads))
        buckets[i].extend(members)
        loads[i] += w
    for b in buckets:
        b.sort()
        if "index.qmd" in b:
            b.remove("index.qmd")
            b.insert(0, "index.qmd")
    return buckets, loads


def page_title(rel):
    """Sidebar text for a page: front-matter title, else first H1, else stem."""
    stem = Path(rel).stem
    try:
        text = (ROOT / rel).read_text(errors="ignore")
    except OSError:
        return stem
    body = text.lstrip("﻿ \t\r\n")
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            m = FRONT_MATTER_TITLE_RE.search(body[3:end])
            if m:
                title = m.group(1).strip()
                if len(title) >= 2 and title[0] == title[-1] and title[0] in "\"'":
                    title = title[1:-1]
                if title:
                    return title
            body = body[end + 4:]
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = H1_RE.match(line)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return stem


def transform_sidebar_items(text, project_files):
    """Convert bare qmd sidebar entries to explicit {text, href} pairs.

    Entries not in the project's render file list (case-sensitive; e.g.
    stale case-mismatched paths on case-insensitive filesystems) are left
    bare so Quarto prunes them in every shard, as in a full render.
    """

    def repl(m):
        indent, rel = m.group(1), m.group(2)
        if rel not in project_files:
            return m.group(0)
        title = page_title(rel).replace("\\", "\\\\").replace('"', '\\"')
        href = "/" + rel[: -len(".qmd")] + ".html"
        return f'{indent}- text: "{title}"\n{indent}  href: {href}'

    return BARE_QMD_ITEM_RE.sub(repl, text)


def website_sidebar_span(text):
    """(start, end) of the website: -> sidebar: block content in _quarto.yml."""
    mw = re.search(r"^website:[ \t]*\n", text, re.M)
    if mw is None:
        return None
    mnext = re.compile(r"^\S", re.M).search(text, mw.end())
    wend = mnext.start() if mnext else len(text)
    ms = re.compile(r"^  sidebar:[ \t]*\n", re.M).search(text, mw.end())
    if ms is None or ms.start() >= wend:
        return None
    mend = re.compile(r"^ {0,2}\S", re.M).search(text, ms.end())
    send = mend.start() if mend and mend.start() <= wend else wend
    return ms.end(), send


def metadata_files(text):
    m = METADATA_FILES_RE.search(text)
    if m is None:
        return []
    return [line.strip()[2:].strip() for line in m.group(1).splitlines()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, required=True, help="1-based shard index")
    ap.add_argument("--count", type=int, required=True, help="total shards")
    args = ap.parse_args()
    if not (1 <= args.shard <= args.count):
        sys.exit(f"ci-shard: --shard must be in 1..{args.count}")

    if args.count == 1:
        print("shard 1/1: full render, no files modified")
        return

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
    new_text = text[: m.start()] + block + text[m.end():]

    # Keep Quarto from pruning sidebar entries for pages outside this shard:
    # convert bare qmd sidebar items to explicit text/href pairs.
    project_files = set(files)
    span = website_sidebar_span(new_text)
    if span is not None:
        s, e = span
        new_text = (
            new_text[:s]
            + transform_sidebar_items(new_text[s:e], project_files)
            + new_text[e:]
        )
    QUARTO_YML.write_text(new_text)
    for mf in metadata_files(new_text):
        p = ROOT / mf
        if p.exists():
            p.write_text(transform_sidebar_items(p.read_text(), project_files))

    print(f"shard {args.shard}/{args.count}: {len(mine)} files, weight {loads[args.shard - 1]}")


if __name__ == "__main__":
    main()
