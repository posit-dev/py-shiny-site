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

import os
import re
import tempfile
from contextlib import contextmanager
from inspect import signature
from pathlib import Path
from typing import Callable, Sequence

import pytest
from playwright.sync_api import BrowserType, ConsoleMessage, Page, expect

from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc, run_shiny_app

FILE_MARKER = re.compile(r"^## file: (.+)$", re.MULTILINE)


@pytest.fixture(scope="session")
def connect_options() -> dict[str, str] | None:
    """Connect to a remote Playwright server when one is configured.

    pytest-playwright's built-in ``launch_browser`` fixture connects to a
    running server (instead of launching a local browser) only when this
    fixture returns non-``None``. CI sets ``PW_TEST_CONNECT_WS_ENDPOINT`` to a
    Dockerized Playwright server (see ``.github/internal/setup-playwright-remote``);
    locally the var is unset, so we launch a local browser as usual.

    Ported from py-shiny's ``tests/playwright/conftest.py``.
    """
    ws_endpoint = os.getenv("PW_TEST_CONNECT_WS_ENDPOINT")
    if not ws_endpoint:
        return None

    endpoint_arg = (
        "endpoint"
        if "endpoint" in signature(BrowserType.connect).parameters
        else "ws_endpoint"
    )
    options = {endpoint_arg: ws_endpoint}
    expose_network = os.getenv("PW_TEST_CONNECT_EXPOSE_NETWORK")
    if expose_network:
        options["expose_network"] = expose_network

    return options


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


# Ported from py-shiny's tests/playwright/examples/example_apps.py (not shipped
# in the installed package). Resolves once Shiny has been idle for `duration`ms.
_WAIT_FOR_IDLE_JS = """
    () => {
        let duration = %s;
        let timeout = %s;
        return new Promise((resolve, reject) => {
            const cleanup = () => {
                $(document).off('shiny:busy', busyFn);
                $(document).off('shiny:idle', idleFn);
                clearTimeout(timeoutId);
                clearTimeout(idleId);
            };
            let timeoutId = setTimeout(() => {
                cleanup();
                reject('Shiny did not become stable within ' + timeout + 'ms');
            }, +timeout);
            let idleId = null;
            const busyFn = () => { clearTimeout(idleId); };
            const idleFn = () => {
                idleId = setTimeout(() => { cleanup(); resolve(); }, +duration);
            };
            $(document).on('shiny:busy', busyFn);
            $(document).on('shiny:idle', idleFn);
            if (!$('html').hasClass('shiny-busy')) { idleFn(); }
        });
    }
"""

# Default benign stderr lines (Express prints this on startup).
_DEFAULT_ALLOW_STDERR = ("Detected Shiny Express app.",)


def create_example_fixture(app_path, *, scope: str = "module"):
    """Return a fixture that launches a raw example app.

    Multi-file ``## file:`` shinylive apps are split into a temp dir first;
    single-file apps (including a lone leading ``## file: app.py`` comment) are
    launched directly. Delegates to the public ``create_app_fixture``.
    """
    app_path = Path(app_path)
    text = app_path.read_text()
    if _num_file_sections(text) > 1:
        launch_dir = Path(tempfile.mkdtemp(prefix="shiny-example-"))
        launch_path = split_shinylive_app(text, launch_dir)
    else:
        launch_path = app_path
    return create_app_fixture(launch_path, scope=scope)


@pytest.fixture
def smoke_test() -> Callable[..., None]:
    def smoke(
        page: Page,
        app: ShinyAppProc,
        *,
        allow_stderr: Sequence[str] = (),
        allow_js: Sequence[str] = (),
    ) -> None:
        console_errors: list[str] = []

        def on_console(msg: ConsoleMessage) -> None:
            if msg.type == "error" and not msg.location["url"].endswith("favicon.ico"):
                console_errors.append(msg.text)

        page.on("console", on_console)
        page.goto(app.url)
        page.evaluate(_WAIT_FOR_IDLE_JS % (300, 30 * 1000))

        allowed = ("INFO:", *_DEFAULT_ALLOW_STDERR, *allow_stderr)
        stderr_errors = [
            line
            for line in str(app.stderr).splitlines()
            if line.strip() and not any(a in line for a in allowed)
        ]
        assert not stderr_errors, "Server stderr errors:\n" + "\n".join(stderr_errors)

        js_errors = [e for e in console_errors if not any(a in e for a in allow_js)]
        assert not js_errors, "JS console errors:\n" + "\n".join(js_errors)

        expect(page.locator(".shiny-output-error")).to_have_count(0)

    return smoke


COMPONENTS_DIR = Path(__file__).parent


def example_app_paths() -> list[Path]:
    """Every example app under ``components/`` (``app.py`` or ``app-*.py``).

    Example apps follow the naming convention ``app.py`` / ``app-<name>.py``;
    build scripts and other ``.py`` files are deliberately excluded.
    """
    paths = set(COMPONENTS_DIR.rglob("app.py")) | set(COMPONENTS_DIR.rglob("app-*.py"))
    return sorted(p for p in paths if "static" not in p.parts)


@contextmanager
def launch_example_app(app_path: Path):
    """Launch a raw example app (splitting multi-file ``## file:`` apps first)."""
    text = Path(app_path).read_text()
    if _num_file_sections(text) > 1:
        launch_path = split_shinylive_app(text, Path(tempfile.mkdtemp(prefix="shiny-example-")))
    else:
        launch_path = Path(app_path)
    with run_shiny_app(launch_path, wait_for_start=True) as proc:
        yield proc
