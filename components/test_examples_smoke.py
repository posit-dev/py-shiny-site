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

_COMPONENTS = Path(__file__).parent
_APPS = example_app_paths()

# Guard against a broken discovery glob silently collecting zero apps (which would
# make the smoke suite "pass" by testing nothing). There are ~308 example apps today;
# any regression that drops us below 300 should fail loudly at collection time.
assert len(_APPS) > 300, (
    f"Expected >300 example apps under components/, found {len(_APPS)}. "
    "Discovery in example_app_paths() may be broken."
)

# App id (path relative to components/) -> stderr substrings to tolerate for that
# app (e.g. a known deprecation an example intentionally still demonstrates).
# Deprecations are otherwise treated as errors.
#
# great_tables.shiny still implements render_gt via py-shiny's legacy
# output_transformer(), which emits a ShinyDeprecationWarning at startup. The
# warning comes from the great-tables package, not the example code; drop these
# entries once great-tables moves to shiny.render.renderer.Renderer.
_GREAT_TABLES_DEPRECATION = [
    "ShinyDeprecationWarning: `shiny.render.transformer.output_transformer()`",
    "super().__init__(",
]
ALLOW_STDERR: dict[str, list[str]] = {
    "outputs/great-tables/app-core.py": _GREAT_TABLES_DEPRECATION,
    "outputs/great-tables/app-detail-preview.py": _GREAT_TABLES_DEPRECATION,
    "outputs/great-tables/app-express.py": _GREAT_TABLES_DEPRECATION,
}


@pytest.mark.parametrize(
    "app_path",
    [pytest.param(p, id=str(p.relative_to(_COMPONENTS))) for p in _APPS],
)
def test_example_app_smoke(page: Page, app_path: Path, smoke_test) -> None:
    rel = str(app_path.relative_to(_COMPONENTS))
    with launch_example_app(app_path) as app:
        smoke_test(page, app, allow_stderr=ALLOW_STDERR.get(rel, ()))
