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

import os
import re

API_BASE_URL = "https://shiny.posit.co/py/api/core"


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

SKIP_TITLES: set[str] = _EXTERNAL | _CHAT_INSTANCE


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
    joined = joined.replace(", )", ")").replace(",)", ")")
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
    title: str, api_dir: str | os.PathLike = "api/core"
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
