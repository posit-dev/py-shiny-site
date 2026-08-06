#!/usr/bin/env python3
"""Merge per-shard Quarto build outputs into one site.

Overlays each shard directory into --out (later shards overwrite duplicate
shared resources, which are identical), then rebuilds the two artifacts that
are per-shard partial: search.json (concatenate arrays) and llms.txt
(header from the first shard that has one + deduplicated entry lines).

Two sharding artifacts are corrected during the merge:

1. Root index.html redirect stubs: a shard whose render list lacks index.qmd
   emits a redirect stub at the site root; only the shard that rendered
   index.qmd has the real homepage. Stubs must not clobber the real page.
2. Cross-shard links: Quarto leaves hrefs pointing at files outside the
   shard's render list as ".qmd"; rewrite relative .qmd hrefs to .html.
"""

import argparse
import json
import re
import shutil
from pathlib import Path

QMD_HREF = re.compile(r'href="(?!https?://)([^":]*)\.qmd(["#])')


def is_redirect_stub(path: Path) -> bool:
    if not path.exists():
        return False
    head = path.read_bytes()[:300].decode("utf-8", "replace")
    return "<title>Redirect to " in head


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", required=True, help="directory containing one subdir per shard")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    shard_dirs = sorted(p for p in Path(args.shards).iterdir() if p.is_dir())
    if not shard_dirs:
        raise SystemExit("ci-merge: no shard directories found")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    search = []
    llms_header = None
    llms_entries = []
    for d in shard_dirs:
        sj = d / "search.json"
        if sj.exists():
            search.extend(json.loads(sj.read_text()))
        lt = d / "llms.txt"
        if lt.exists():
            lines = lt.read_text().splitlines()
            first = next((i for i, l in enumerate(lines) if l.startswith("- ")), len(lines))
            if llms_header is None:
                llms_header = lines[:first]
            llms_entries.extend(l for l in lines[first:] if l.startswith("- "))

        # Overlay the shard, but keep root index.html redirect stubs from
        # clobbering the real homepage (copied separately below).
        def ignore_root_index(src, names):
            if Path(src) == d and "index.html" in names:
                return {"index.html"}
            return set()

        shutil.copytree(d, out, dirs_exist_ok=True, ignore=ignore_root_index)
        shard_index = d / "index.html"
        out_index = out / "index.html"
        if shard_index.exists() and (
            not is_redirect_stub(shard_index) or not out_index.exists()
        ):
            shutil.copy2(shard_index, out_index)

    if is_redirect_stub(out / "index.html"):
        raise SystemExit(
            "ci-merge: root index.html is still a redirect stub; "
            "no shard rendered the real homepage"
        )

    # Resolve cross-shard links Quarto left as .qmd hrefs.
    rewritten = 0
    for p in out.rglob("*.html"):
        if "site_libs" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="surrogateescape")
        new, n = QMD_HREF.subn(r'href="\1.html\2', text)
        if n:
            p.write_text(new, encoding="utf-8", errors="surrogateescape")
            rewritten += n

    (out / "search.json").write_text(json.dumps(search))
    uniq = list(dict.fromkeys(llms_entries))
    if llms_header is not None:
        (out / "llms.txt").write_text("\n".join(llms_header + uniq) + "\n")
    print(
        f"ci-merge: {len(shard_dirs)} shards, {len(search)} search entries, "
        f"{len(uniq)} llms entries, {rewritten} .qmd hrefs resolved"
    )


if __name__ == "__main__":
    main()
