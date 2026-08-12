#!/usr/bin/env python3
"""Check a rendered site for broken internal links.

Scans every ``*.html`` under the render directory (default ``_build``) and
reports ``href``/``src`` targets that do not resolve on disk, plus any ``.qmd``
href that survived rendering.

Quarto validates ``.qmd`` links, but only those: a link with no extension (e.g.
``templates/dashboard/``) is passed through verbatim, so a missing leading slash
silently 404s. This catches that class, along with stale hand-written ``.html``
paths and unresolved fragments.

Usage::

    scripts/check-page-links.py [--dir _build] [--allow FILE] [--anchors]

Exits 1 if anything is reported.

``--anchors`` is opt-in. quartodoc emits interlinks like
``api/core/App.html#shiny.App`` but no matching ``id`` attribute on the target
page, so enabling it reports ~1500 findings from generated ``api/**`` output.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from urllib.parse import unquote, urlsplit

# Attribute values we resolve. Deliberately not `srcset` (comma/width syntax).
ATTR_RE = re.compile(r'(?:href|src)="([^"]*)"')

# Regions whose contents are illustrative or client-side, not site links:
# code samples name things like `my-styles.css`, and JS/EJS templates carry
# placeholders (`${href}`, `<%= app.shinylive %>`) that are not URLs at all.
INERT_RE = re.compile(r"<pre\b.*?</pre>|<code\b.*?</code>|<script\b.*?</script>", re.S)

# Anything not resolved against the filesystem.
EXTERNAL_RE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.I)
TEMPLATE_RE = re.compile(r"[<$]%?[={]|\{\{")

# Content-hashed asset paths differ between shard outputs; the merge step owns
# reconciling them, and a stale local render trips over them constantly.
SKIP_PATH_RE = re.compile(r"(^|/)site_libs/")

ANCHOR_ID_RE = re.compile(r'\bid="([^"]+)"')
ANCHOR_NAME_RE = re.compile(r'\bname="([^"]+)"')


@dataclass(frozen=True)
class Finding:
    kind: str
    target: str
    source: str

    def __str__(self) -> str:
        return f"{self.kind:<14} {self.target}\n{'':<14} in {self.source}"


def load_allowlist(path: str | None) -> set[str]:
    """Read newline-separated ``kind<TAB>target`` entries.

    Only a leading ``#`` starts a comment -- entries routinely end in a URL
    fragment (``page.html#anchor``), so mid-line ``#`` is data, not a comment.
    """
    if not path:
        return set()
    allowed = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                allowed.add(line)
    return allowed


def anchors_of(path: str, cache: dict[str, set[str]]) -> set[str]:
    if path not in cache:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                html = fh.read()
        except OSError:
            cache[path] = set()
        else:
            cache[path] = set(ANCHOR_ID_RE.findall(html)) | set(
                ANCHOR_NAME_RE.findall(html)
            )
    return cache[path]


def resolve(root: str, page_dir: str, path: str) -> str | None:
    """Map a link path to the file that would serve it, or None if nothing does."""
    if path.startswith("/"):
        base = os.path.join(root, path.lstrip("/"))
    else:
        base = os.path.join(page_dir, path)
    base = os.path.normpath(base)
    if os.path.isdir(base):
        index = os.path.join(base, "index.html")
        return index if os.path.isfile(index) else None
    return base if os.path.isfile(base) else None


def check(root: str, check_anchors: bool) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    anchor_cache: dict[str, set[str]] = {}
    pages = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {"site_libs", ".venv"}]
        for filename in sorted(filenames):
            if not filename.endswith(".html"):
                continue
            pages += 1
            page = os.path.join(dirpath, filename)
            rel_page = os.path.relpath(page, root)
            with open(page, encoding="utf-8", errors="replace") as fh:
                html = INERT_RE.sub("", fh.read())

            for raw in dict.fromkeys(ATTR_RE.findall(html)):
                value = raw.strip()
                if (
                    not value
                    or value.startswith("#")
                    or EXTERNAL_RE.match(value)
                    or TEMPLATE_RE.search(value)
                    or SKIP_PATH_RE.search(value)
                ):
                    continue

                split = urlsplit(value)
                path = unquote(split.path)
                if not path:
                    continue

                # A .qmd href in rendered output means Quarto (or the shard
                # merge) failed to rewrite it: the reader gets served source.
                if path.endswith(".qmd"):
                    findings.append(Finding("unrewritten-qmd", value, rel_page))
                    continue

                target = resolve(root, dirpath, path)
                if target is None:
                    findings.append(Finding("missing-target", value, rel_page))
                    continue

                if check_anchors and split.fragment:
                    fragment = unquote(split.fragment)
                    if fragment not in anchors_of(target, anchor_cache):
                        findings.append(Finding("missing-anchor", value, rel_page))

    return findings, pages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="_build", help="rendered site (default: _build)")
    parser.add_argument("--allow", help="allowlist file of known-broken entries")
    parser.add_argument(
        "--anchors",
        action="store_true",
        help=(
            "also check #fragments. Off by default: quartodoc does not emit "
            "id attributes for the objects its own interlinks target, so this "
            "currently reports ~1500 findings from generated api/** pages."
        ),
    )
    args = parser.parse_args(argv)

    root = os.path.normpath(args.dir)
    if not os.path.isdir(root):
        print(f"error: no such render directory: {root}", file=sys.stderr)
        print("Build the site first (e.g. `make site-parallel`).", file=sys.stderr)
        return 2

    findings, pages = check(root, check_anchors=args.anchors)

    allowed = load_allowlist(args.allow)
    kept = [f for f in findings if f"{f.kind}\t{f.target}" not in allowed]
    suppressed = len(findings) - len(kept)

    by_kind: dict[str, list[Finding]] = defaultdict(list)
    for finding in kept:
        by_kind[finding.kind].append(finding)

    print(f"Scanned {pages} pages in {root}/")
    if suppressed:
        print(f"Suppressed {suppressed} allowlisted finding(s) from {args.allow}")

    if not kept:
        print("No broken internal links found.")
        return 0

    for kind in sorted(by_kind):
        group = by_kind[kind]
        print(f"\n{kind} ({len(group)}):")
        for finding in sorted(group, key=lambda f: (f.target, f.source)):
            print(f"  {finding.target}\n      in {finding.source}")

    print(f"\n{len(kept)} broken internal link(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
