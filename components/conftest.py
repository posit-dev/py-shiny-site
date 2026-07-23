"""Shared pytest fixtures and helpers for component example-app tests.

These tests launch the raw ``app-*.py`` example files (the source of truth for
each component page; the shinylive links are generated from them) and verify
they run without server, JavaScript, or output errors, plus drive their widgets
via py-shiny's public Playwright controllers.

Only the public ``shiny`` package API is used:
``shiny.pytest.create_app_fixture``, ``shiny.playwright.controller`` and
``shiny.run.ShinyAppProc``.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

FILE_MARKER = re.compile(r"^## file: (.+)$", re.MULTILINE)


def _num_file_sections(text: str) -> int:
    """Number of ``## file: NAME`` section markers in a shinylive source."""
    return len(FILE_MARKER.findall(text))


def split_shinylive_app(text: str, dest: Path) -> Path:
    """Split a multi-file shinylive source into real files under ``dest``.

    Each ``## file: NAME`` marker starts a new file. Returns the path to the
    entry ``app.py`` so the caller can launch it with ``shiny run``.
    """
    matches = list(FILE_MARKER.finditer(text))
    for i, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end() + 1  # skip the newline after the marker line
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        (dest / name).write_text(text[start:end])
    return dest / "app.py"
