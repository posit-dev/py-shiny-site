"""Resolve relevant-functions title -> (href, signature) from generated API pages.

The quartodoc-generated ``api/core/*.qmd`` pages are the single source of truth:
each documented object renders a ``{ #shiny.<qualified-name> }`` anchor followed
by a fenced ``python`` code block holding the exact signature convention (param
names + defaults, annotations stripped). We parse that rather than re-deriving
the convention from ``inspect.signature``.

Resolution is core-consistent: always ``api/core`` (never the express page,
which renders a different context-manager signature).
"""

from __future__ import annotations

import logging
import os
import re

from _qmd import get_qmd_split, write_qmd

lg = logging.getLogger("relevant-functions")

API_BASE_URL = "https://shiny.posit.co/py/api/core"

# Anchor default paths to the repo root (parent of this file's ``components/``
# dir) so discovery and API-page lookup work regardless of the current working
# directory -- pytest run from the repo root, the CLI, or ``cd components``.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_API_DIR = os.path.join(_REPO_ROOT, "api", "core")


class TitleResolutionError(Exception):
    """A relevant-functions ``title`` could not be resolved to an API page."""


# Titles intentionally NOT generated (left hand-authored). Grouped by reason so
# the list stays reviewable.

# External packages with no page in this site's api/ tree.
_EXTERNAL = {
    "@shinywidgets.render_widget()",
    "shinywidgets.output_widget",
}

# Chat is documented against an *instance* (``chat = ui.Chat()``) so its titles
# use instance/decorator forms that intentionally differ from the class API.
_CHAT_INSTANCE = {
    "@chat.on_user_submit",
    "chat = ui.Chat()",
    "chat.append_message()",
    "chat.append_message_stream()",
    "chat.ui()",
}

# Transitional: these resolve once the py-shiny submodule bump lands (see
# posit-dev/py-shiny-site#404). Until then the pinned submodule has no API page
# for them, so leave their hand-authored fields untouched instead of erroring.
# Remove from this set once #404 is merged (card_body gains an api/ page;
# panel_well's dead link is dropped).
_PENDING_SUBMODULE_BUMP = {
    "ui.card_body",
    "ui.panel_well",
}

SKIP_TITLES: set[str] = _EXTERNAL | _CHAT_INSTANCE | _PENDING_SUBMODULE_BUMP


def normalize_title(title: str) -> str:
    """Strip a leading ``@``, a trailing ``(...)``, and a leading ``express.``."""
    t = title.strip()
    if t.startswith("@"):
        t = t[1:]
    t = t.split("(", 1)[0].strip()
    if t.startswith("express."):
        t = t[len("express.") :]
    return t


def flatten_python_block(block: str) -> str:
    """Collapse a multi-line rendered signature into one logical line."""
    # Join every line, drop indentation/newlines, normalize inter-arg spacing.
    joined = " ".join(line.strip() for line in block.strip().splitlines())
    joined = re.sub(r"\s+", " ", joined)
    # Remove a space after "(" and before ")", and the trailing comma before ")".
    joined = joined.replace("( ", "(").replace(" )", ")")
    # Strip only the trailing separator comma before the final ")".
    joined = re.sub(r",\s*\)$", ")", joined)
    return joined.strip()


def extract_signature_block(qmd_text: str, anchor: str) -> str:
    """Flattened signature for the section whose header carries ``{ #anchor }``."""
    marker = f"{{ #{anchor} }}"
    idx = qmd_text.find(marker)
    if idx == -1:
        raise TitleResolutionError(
            f"anchor '{marker}' not found in API page for '{anchor}'"
        )
    fence = re.search(r"```python\n(.*?)\n```", qmd_text[idx:], re.DOTALL)
    if fence is None:
        raise TitleResolutionError(
            f"no python signature block after anchor '{marker}'"
        )
    return flatten_python_block(fence.group(1))


def _href(file_stem: str, anchor: str) -> str:
    return f"{API_BASE_URL}/{file_stem}.html#{anchor}"


def resolve_title(
    title: str, api_dir: str | os.PathLike = DEFAULT_API_DIR
) -> tuple[str, str]:
    """Return ``(href, signature)`` for ``title``; raise if unresolvable."""
    name = normalize_title(title)
    anchor = f"shiny.{name}"
    api_dir = os.fspath(api_dir)

    # 1. Top-level object: its own qmd file.
    own = os.path.join(api_dir, f"{name}.qmd")
    if os.path.isfile(own):
        sig = extract_signature_block(_read(own), anchor)
        return _href(name, anchor), sig

    # 2. Method: <Class>.<method> lives on the class file with a section anchor.
    if "." in name:
        parent = name.rsplit(".", 1)[0]
        cls = os.path.join(api_dir, f"{parent}.qmd")
        if os.path.isfile(cls):
            sig = extract_signature_block(_read(cls), anchor)
            return _href(parent, anchor), sig

    raise TitleResolutionError(
        f"title '{title}' -> '{name}': no API page at '{own}' "
        f"(nor a class file for a method). Add it to SKIP_TITLES if intentional."
    )


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


_COMPONENT_DIRS = tuple(
    os.path.join(_REPO_ROOT, "components", d)
    for d in ("inputs", "outputs", "display-messages", "layout")
)
_LAYOUT_DIRS = (os.path.join(_REPO_ROOT, "layouts"),)


def find_index_qmds() -> list[str]:
    """Every component + layout ``index.qmd`` (leaf pages)."""
    out: list[str] = []
    for base in (*_COMPONENT_DIRS, *_LAYOUT_DIRS):
        if not os.path.isdir(base):
            continue
        for entry in sorted(os.listdir(base)):
            cdir = os.path.join(base, entry)
            if not os.path.isdir(cdir) or ".ruff_cache" in cdir:
                continue
            qmd = os.path.join(cdir, "index.qmd")
            if os.path.isfile(qmd):
                out.append(qmd)
    return out


def resolve_index_qmds(paths: list[str]) -> list[str]:
    """Map dirs / files / index.qmd paths to their owning ``index.qmd``."""
    out: list[str] = []
    seen: set[str] = set()
    for path in paths:
        path = os.path.normpath(path)
        if os.path.isdir(path):
            qmd = os.path.join(path, "index.qmd")
        elif os.path.basename(path) == "index.qmd":
            qmd = path
        else:
            qmd = os.path.join(os.path.dirname(path), "index.qmd")
        if os.path.isfile(qmd) and qmd not in seen:
            seen.add(qmd)
            out.append(qmd)
    return out


def rewrite_relevant_functions(
    qmd: str,
    api_dir: str | os.PathLike = DEFAULT_API_DIR,
    strict: bool = True,
) -> bool:
    """Rewrite href/signature for every relevant-functions entry in ``qmd``.

    When ``strict`` (the default), an unresolvable title raises
    ``TitleResolutionError``. When not strict, the generator "falls forward":
    an unresolvable title is logged and left as-authored so a single rotted
    entry never aborts a build/setup run. CI runs strict, so the rot is still
    required to be fixed before merge.
    """
    meta, body = get_qmd_split(qmd)
    listing = meta.get("listing")
    if not listing:
        return False
    if isinstance(listing, dict):
        listing = [listing]

    had_block = False
    for block in listing:
        if not (isinstance(block, dict) and block.get("id") == "relevant-functions"):
            continue
        had_block = True
        for item in block.get("contents") or []:
            title = str(item.get("title", ""))
            if title in SKIP_TITLES:
                continue
            try:
                href, signature = resolve_title(title, api_dir=api_dir)
            except TitleResolutionError as err:
                if strict:
                    raise
                lg.warning(f"{qmd}: leaving unresolvable title as-authored: {err}")
                continue
            item["href"] = href
            item["signature"] = signature

    if had_block:
        write_qmd((meta, body), qmd)
    return had_block
