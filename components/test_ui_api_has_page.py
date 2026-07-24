"""Verify every public ``ui`` export is documented by a component page.

Each public function in ``shiny.ui.__all__`` and ``shiny.express.ui.__all__``
should either be documented by a component page under ``components/`` -- listed
in that page's ``relevant-functions`` front-matter block -- or be named in the
``KNOWN_MISSING_COMPONENTS`` opt-out set below. A newly added ``ui`` export that
is neither fails ``test_every_ui_export_has_a_page``, forcing a conscious
"add a component page or opt out" decision.

Coverage is read from the ``relevant-functions`` listing block already present in
each ``components/**/index.qmd`` front matter (its ``title:`` entries name the
documented functions, e.g. ``ui.input_action_button``); no dedicated registry is
needed.

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

# Mutators: ``update_*`` / ``insert_*`` / ``remove_*``. Documented on their base
# component's page, which is enforced separately by that page existing.
_MUTATORS = {
    "insert_nav_panel", "insert_ui", "remove_nav_panel", "remove_ui",
    "update_action_button", "update_action_link", "update_checkbox",
    "update_checkbox_group", "update_code_editor", "update_dark_mode",
    "update_date", "update_date_range", "update_nav_panel", "update_navs",
    "update_navset", "update_numeric", "update_popover", "update_radio_buttons",
    "update_select", "update_selectize", "update_sidebar", "update_slider",
    "update_submit_textarea", "update_switch", "update_task_button",
    "update_text", "update_text_area",
}

# Layout / navigation / page / panel functions -- documented in ``layouts/``.
_LAYOUT = {
    "column", "row", "layout_column_wrap", "layout_columns", "layout_sidebar",
    "sidebar", "nav_control", "nav_menu", "nav_panel", "nav_spacer",
    "navbar_options", "navset_bar", "navset_card_pill", "navset_card_tab",
    "navset_card_underline", "navset_hidden", "navset_pill", "navset_pill_list",
    "navset_tab", "navset_underline", "page_auto", "page_bootstrap",
    "page_fillable", "page_fixed", "page_fluid", "page_navbar", "page_opts",
    "page_output", "page_sidebar", "panel_absolute", "panel_conditional",
    "panel_fixed", "panel_title", "panel_well", "showcase_bottom",
    "showcase_left_center", "showcase_top_right", "value_box_theme",
}

# Express-only / low-level helpers with no standalone component page.
_MISC = {"busy_indicators", "fill", "hold"}

# TODO: genuine components that should get their own component page. Move each
# to a real page (and drop it from here) as pages are written.
_TODO_NEEDS_PAGE = {
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
    | _LAYOUT
    | _MISC
    | _TODO_NEEDS_PAGE
)


def _documented_functions() -> set[str]:
    """``ui`` function names named by any page's ``relevant-functions`` block."""
    names: set[str] = set()
    for qmd in COMPONENTS_DIR.glob("**/index.qmd"):
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
        f"These shiny.ui / shiny.express.ui exports have no component page: "
        f"{sorted(missing)}.\n"
        "For each: add it to a component page's `relevant-functions` front-matter "
        "block, or add it to KNOWN_MISSING_COMPONENTS in this file (with the "
        "right category group)."
    )
