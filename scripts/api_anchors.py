"""Restore the object anchors that Quarto drops from generated ``api/**`` pages.

quartodoc writes an explicit anchor onto every documented object's heading
(``# App { #shiny.App }``) and records the resulting URL in ``objects.json``,
the interlink inventory that every ``:func:``/``:class:`` reference in a
docstring resolves through. Two things then break that contract:

1. **The page's own object loses its id.** Its heading is the first ``#`` in the
   file, so Quarto promotes it into the title block -- and drops the attributes,
   including the id. ``api/core/App.html`` ends up with ``#shiny.App.run`` and
   friends but no ``#shiny.App``. This is the bulk of it: 290 of the 293 dead
   fragments on the site.

2. **Re-export aliases don't match.** The inventory advertises the public path
   (``shiny.Session.close``) while the page is generated from the canonical one
   (``shiny.session.Session.close``), so the heading id and the link disagree.

Both leave the reader at the top of the page instead of at the definition, and
neither is visible to Quarto's own link checking, which only validates ``.qmd``
links. This module closes the gap by post-processing the rendered HTML: where a
promised fragment is missing, it injects an empty ``<span>`` carrying that id at
the right place.

Three rules decide what to add, in order of how directly the evidence ties an
anchor to a location:

``own-heading``
    The sibling ``.qmd``'s first heading carries ``{ #path }`` but the HTML has
    no such id -- exactly the id Quarto swallowed. Goes on the title block,
    which is what that heading became.
``primary-object``
    The inventory promises ``<page>#shiny.<page stem>``. Covers pages whose qmd
    has no id to read because the object is spread over the page rather than
    titling it (``api/core/Session.qmd`` starts with a bare ``# Session``).
``alias``
    The inventory promises a path whose final two segments uniquely match an id
    already on the page -- a re-export of the same object. Goes on that element,
    so the link still lands on the definition rather than the page top.

It deliberately adds nothing that neither the page nor the inventory already
promised. An undocumented object that something links to stays broken, because
that is a real documentation bug and ``scripts/site_links.py --anchors`` should
keep reporting it.

Run as part of ``scripts/post-render.py``, or standalone against a built site:

    python3 scripts/api_anchors.py --dir _build [--source .] [--inventory objects.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from dataclasses import dataclass, field

# Generated Quarto output quotes attributes consistently, so regexes are enough
# here and keep this dependency-free -- the same tradeoff scripts/site_links.py
# makes.
ID_RE = re.compile(r'\bid="([^"]+)"')
TITLE_BLOCK_RE = re.compile(r'<header\s+id="title-block-header"[^>]*>')
# quartodoc's heading anchor, e.g. `# App { #shiny.App }`.
QMD_HEADING_ID_RE = re.compile(r"^#\s+\S.*?\{\s*#(\S+?)\s*\}\s*$")

# Object paths, as opposed to Quarto's own chrome ids ("quarto-content",
# "parameters", ...). Every anchor quartodoc emits is a dotted Python path.
OBJECT_ID_PREFIX = "shiny."


def existing_ids(html: str) -> set[str]:
    return set(ID_RE.findall(html))


def qmd_heading_id(qmd_path: str) -> str | None:
    """The explicit anchor on a generated page's first heading, if it has one."""
    try:
        with open(qmd_path, encoding="utf-8") as f:
            first_line = f.readline()
    except OSError:
        return None
    m = QMD_HEADING_ID_RE.match(first_line.strip())
    return m.group(1) if m else None


def inventory_fragments(inventory_path: str) -> dict[str, set[str]]:
    """Map each page's site-relative path to the fragments the inventory promises."""
    with open(inventory_path, encoding="utf-8") as f:
        items = json.load(f)["items"]

    pages: dict[str, set[str]] = {}
    for item in items:
        page, _, fragment = item["uri"].partition("#")
        if fragment:
            pages.setdefault(page, set()).add(fragment)
    return pages


def _element_start(html: str, anchor_id: str) -> int | None:
    """Offset of the opening tag of the element carrying ``anchor_id``."""
    m = re.search(r"<[a-zA-Z][^>]*\bid=\"" + re.escape(anchor_id) + r'"', html)
    return None if m is None else m.start()


def _alias_target(html: str, ids: set[str], fragment: str) -> int | None:
    """Offset of the heading documenting the same object under another path.

    Requires a unique match on the final two path segments, so this never
    guesses; an ambiguous tail is left for the link checker to report.
    """
    tail = ".".join(fragment.split(".")[-2:])
    candidates = [
        i
        for i in ids
        if i.startswith(OBJECT_ID_PREFIX) and ".".join(i.split(".")[-2:]) == tail
    ]
    if len(candidates) != 1:
        return None
    return _element_start(html, candidates[0])


def plan_anchors(
    page: str,
    html: str,
    own_heading_id: str | None,
    promised: set[str],
) -> tuple[list[tuple[str, int, str]], list[str]]:
    """Decide where each missing anchor goes.

    Returns ``(insertions, unresolved)``, where an insertion is
    ``(fragment, offset, rule)``.
    """
    ids = existing_ids(html)
    stem = os.path.basename(page).removesuffix(".html")
    title_block = TITLE_BLOCK_RE.search(html)

    # The page's own object, by either route. Both land on the title block, so
    # order only decides which rule gets the credit in the report.
    wanted: list[tuple[str, str]] = []
    if own_heading_id is not None:
        wanted.append((own_heading_id, "own-heading"))
    if (primary := OBJECT_ID_PREFIX + stem) != own_heading_id:
        if primary in promised:
            wanted.append((primary, "primary-object"))
    wanted += [(f, "alias") for f in sorted(promised) if f not in dict(wanted)]

    insertions: list[tuple[str, int, str]] = []
    unresolved: list[str] = []
    for fragment, rule in wanted:
        if fragment in ids:
            continue
        if rule == "alias":
            offset = _alias_target(html, ids, fragment)
        else:
            offset = None if title_block is None else title_block.end()
        if offset is None:
            unresolved.append(fragment)
        else:
            insertions.append((fragment, offset, rule))

    return insertions, unresolved


def apply_anchors(html: str, insertions: list[tuple[str, int, str]]) -> str:
    """Inject the planned anchors. Applied back-to-front so offsets stay valid."""
    for fragment, offset, _rule in sorted(insertions, key=lambda p: p[1], reverse=True):
        html = f'{html[:offset]}<span id="{fragment}"></span>{html[offset:]}'
    return html


@dataclass
class Report:
    pages_changed: int = 0
    by_rule: dict[str, int] = field(default_factory=dict)
    unresolved: list[tuple[str, str]] = field(default_factory=list)

    @property
    def anchors_added(self) -> int:
        return sum(self.by_rule.values())


def ensure_api_anchors(
    build_dir: str,
    source_dir: str = ".",
    inventory_path: str | None = "objects.json",
    prefix: str = "api",
) -> Report:
    """Add every promised anchor missing from the built ``api/**`` pages."""
    report = Report()
    promised_by_page: dict[str, set[str]] = {}
    if inventory_path and os.path.exists(inventory_path):
        promised_by_page = inventory_fragments(inventory_path)

    pattern = os.path.join(build_dir, prefix, "**", "*.html")
    for path in sorted(glob.glob(pattern, recursive=True)):
        page = os.path.relpath(path, build_dir).replace(os.sep, "/")

        with open(path, encoding="utf-8") as f:
            html = f.read()

        insertions, unresolved = plan_anchors(
            page,
            html,
            qmd_heading_id(os.path.join(source_dir, page[: -len(".html")] + ".qmd")),
            promised_by_page.get(page, set()),
        )
        report.unresolved.extend((page, f) for f in unresolved)
        if not insertions:
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write(apply_anchors(html, insertions))
        report.pages_changed += 1
        for _fragment, _offset, rule in insertions:
            report.by_rule[rule] = report.by_rule.get(rule, 0) + 1

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir", default="_build", help="rendered site (default: _build)"
    )
    parser.add_argument(
        "--source",
        default=".",
        help="tree holding the generated api/**/*.qmd (default: .)",
    )
    parser.add_argument(
        "--inventory",
        default="objects.json",
        help="quartodoc interlink inventory (default: objects.json)",
    )
    args = parser.parse_args()

    report = ensure_api_anchors(args.dir, args.source, args.inventory)
    rules = ", ".join(f"{n} {rule}" for rule, n in sorted(report.by_rule.items()))
    print(
        f"api-anchors: added {report.anchors_added} anchor(s) across "
        f"{report.pages_changed} page(s) in {args.dir}" + (f" ({rules})" if rules else "")
    )
    # Not an error: these are inventory entries with no heading to attach to
    # (attributes rendered into a table, undocumented members). They only matter
    # if something links to them, and then site_links.py --anchors reports it.
    if report.unresolved:
        print(f"api-anchors: {len(report.unresolved)} promised anchor(s) had no target")
    return 0


if __name__ == "__main__":
    sys.exit(main())
