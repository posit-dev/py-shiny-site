"""Smoke-test every component example app.

Discovers every ``app.py`` / ``app-*.py`` under ``components/`` and runs each as
its own parametrized test case (test id = the app's path relative to
``components/``), asserting it launches with no server, JS, or output errors.
Interaction tests live in each component's own ``test_<name>.py``.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from conftest import example_app_paths, launch_example_app
from shiny.run import ShinyAppProc

_COMPONENTS = Path(__file__).parent
_APPS = example_app_paths()


@pytest.mark.parametrize(
    "app_path",
    _APPS,
    ids=[str(p.relative_to(_COMPONENTS)) for p in _APPS],
)
def test_example_app_smoke(page: Page, app_path: Path, smoke_test) -> None:
    with launch_example_app(app_path) as app:
        smoke_test(page, app)
