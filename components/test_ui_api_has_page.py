"""Verify every public ``ui`` export is documented by a doc page.

Each public function in ``shiny.ui.__all__`` and ``shiny.express.ui.__all__``
should either be documented by a page under ``components/`` or ``layouts/`` --
listed in that page's ``relevant-functions`` front-matter block -- or be named in
the ``KNOWN_MISSING_COMPONENTS`` opt-out set below. A newly added ``ui`` export
that is neither fails ``test_every_ui_export_has_a_page``, forcing a conscious
"add a doc page or opt out" decision.

Coverage is read from the ``relevant-functions`` listing block already present in
each ``components/**/index.qmd`` and ``layouts/**/index.qmd`` front matter (its
``title:`` entries name the documented functions, e.g.
``ui.input_action_button``); no dedicated registry is needed.

This is a static filesystem check (no browser), so it runs under ``make test-apps``.
It mirrors py-shiny's ``test_express_ui_is_complete`` (explicit opt-out set +
staleness guard).
"""

from __future__ import annotations

import re
from pathlib import Path

import shiny.express.ui
import shiny.ui
import yaml

COMPONENTS_DIR = Path(__file__).parent
REPO_ROOT = COMPONENTS_DIR.parent

# Documentation sections whose pages carry ``relevant-functions`` front matter.
DOC_DIRS = (COMPONENTS_DIR, REPO_ROOT / "layouts")

# Every public ``ui`` export across the Core and Express APIs.
API: set[str] = set(shiny.ui.__all__) | set(shiny.express.ui.__all__)

# ``ui.<name>`` / ``express.ui.<name>`` from a page's ``relevant-functions``
# ``title:`` (also tolerates a trailing ``()``, e.g. ``ui.input_checkbox()``).
_TITLE_RE = re.compile(r"^(?:express\.)?ui\.([A-Za-z_][A-Za-z0-9_]*)")

# ---------------------------------------------------------------------------
# Opt-out set: exports that intentionally have no dedicated component page.
# Grouped by reason so the list stays reviewable. Keep it honest -- the
# staleness guard below fails if any entry is no longer a ``ui`` export.
# ---------------------------------------------------------------------------

# htmltools re-exports and tag / include helpers -- primitives, not components.
_HTMLTOOLS = {
    "HTML", "Tag", "TagList", "a", "br", "code", "div", "em",
    "h1", "h2", "h3", "h4", "h5", "h6", "head_content", "hr", "img", "p",
    "pre", "span", "strong", "tags", "markdown", "include_css", "include_js",
    "js_eval", "help_text",
}

# Type aliases / option types -- not callable components.
_TYPE_ALIASES = {
    "AnimationOptions", "ShowcaseLayout", "SliderStepArg", "SliderValueArg",
    "TagAttrValue", "TagAttrs", "TagChild",
}

# Classes returned/consumed by component functions (documented alongside them).
_CLASSES = {
    "AccordionPanel", "CardItem", "Chat", "MarkdownStream", "Sidebar", "Theme",
    "ValueBoxTheme",
}

# Plot brushing / click option builders.
_OPTS = {"brush_opts", "click_opts", "dblclick_opts", "hover_opts"}

# Mutators (``update_*`` / ``insert_*`` / ``remove_*``) are documented in their
# base component's ``relevant-functions`` block, not opted out. The only ones
# still listed here are those whose base component has no page yet -- their
# mutator should be added to that page's ``relevant-functions`` when it is
# written (the base component is tracked in _TODO_NEEDS_COMPONENT_PAGE).
_MUTATORS = {
    "update_code_editor",       # base: input_code_editor
    "update_popover",           # base: popover
    "update_submit_textarea",   # base: input_submit_textarea
    "update_task_button",       # base: input_task_button
}

# Deprecated / superseded functions that intentionally have no doc page.
_DEPRECATED = {"column", "row"}  # superseded by layout_columns / layout_column_wrap

# TODO: layout / navigation / page / panel functions not yet documented in a
# ``layouts/`` page. The ``layouts/`` files' ``relevant-functions`` blocks are
# the source of truth for layout documentation -- once one of these appears
# there (or on a component page) it is counted, so drop it from this list.
_TODO_NEEDS_LAYOUT_PAGE = {
    "nav_control", "nav_menu", "nav_spacer", "navbar_options",
    "navset_bar", "navset_card_underline", "navset_hidden", "navset_underline",
    "page_auto", "page_bootstrap", "page_fluid", "page_opts", "page_output",
    "page_sidebar", "panel_conditional", "panel_title", "showcase_bottom",
    "showcase_left_center", "showcase_top_right", "value_box_theme",
}

# Express-only / low-level helpers with no standalone component page.
_MISC = {"busy_indicators", "fill", "hold"}

# TODO: genuine components that should get their own component page. Move each
# to a real page (and drop it from here) as pages are written.
_TODO_NEEDS_COMPONENT_PAGE = {
    "bind_task_button", "chat_ui", "download_button", "download_link",
    "input_bookmark_button", "input_code_editor", "input_submit_textarea",
    "input_task_button", "output_code", "output_markdown_stream", "output_table",
    "popover", "toast", "toast_header", "show_toast", "hide_toast",
}

KNOWN_MISSING_COMPONENTS: set[str] = (
    _HTMLTOOLS
    | _TYPE_ALIASES
    | _CLASSES
    | _OPTS
    | _MUTATORS
    | _MISC
    | _DEPRECATED
    | _TODO_NEEDS_LAYOUT_PAGE
    | _TODO_NEEDS_COMPONENT_PAGE
)


def _documented_functions() -> set[str]:
    """``ui`` function names named by any page's ``relevant-functions`` block."""
    names: set[str] = set()
    for doc_dir in DOC_DIRS:
        for qmd in doc_dir.glob("**/index.qmd"):
            text = qmd.read_text()
            if not text.startswith("---"):
                continue
            try:
                front_matter = yaml.safe_load(text.split("---", 2)[1])
            except yaml.YAMLError:
                continue
            if not isinstance(front_matter, dict):
                continue
            listing = front_matter.get("listing") or []
            if isinstance(listing, dict):
                listing = [listing]
            for block in listing:
                if not (isinstance(block, dict) and block.get("id") == "relevant-functions"):
                    continue
                for item in block.get("contents") or []:
                    match = _TITLE_RE.match(str((item or {}).get("title", "")))
                    if match:
                        names.add(match.group(1))
    return names


DOCUMENTED = _documented_functions()


def test_documented_functions_discovered() -> None:
    """Guard against a broken parser silently discovering nothing."""
    assert len(DOCUMENTED) > 40, (
        f"Expected >40 documented ui functions from relevant-functions blocks, "
        f"found {len(DOCUMENTED)}. Front-matter parsing may be broken."
    )


def test_known_missing_are_real_exports() -> None:
    """Keep the opt-out list honest: every entry must still be a ui export."""
    stale = KNOWN_MISSING_COMPONENTS - API
    assert not stale, (
        f"KNOWN_MISSING_COMPONENTS names things that aren't ui exports anymore "
        f"(stale/typo): {sorted(stale)}. Remove them."
    )


def test_documented_functions_are_real_exports() -> None:
    """A relevant-functions entry must name an actual ui export (catch typos)."""
    unknown = DOCUMENTED - API
    assert not unknown, (
        f"relevant-functions blocks reference ui functions that don't exist in "
        f"shiny.ui / shiny.express.ui __all__: {sorted(unknown)}."
    )


def test_every_ui_export_has_a_page() -> None:
    """Every public ui export is documented by a page or explicitly opted out."""
    missing = API - DOCUMENTED - KNOWN_MISSING_COMPONENTS
    assert not missing, (
        f"These shiny.ui / shiny.express.ui exports have no doc page: "
        f"{sorted(missing)}.\n"
        "For each: add it to a components/ or layouts/ page's `relevant-functions` "
        "front-matter block, or add it to KNOWN_MISSING_COMPONENTS in this file "
        "(with the right category group)."
    )
