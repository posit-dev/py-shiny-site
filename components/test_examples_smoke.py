"""Smoke-test every documentation example app.

Discovers every ``app.py`` / ``app-*.py`` under the roots listed in
``conftest.EXAMPLE_APP_DIRS`` (``components/`` and ``layouts/``) and runs each as
its own parametrized test case (test id = the app's path relative to the repo
root), asserting it launches with no server, JS, or output errors. Interaction
tests live in each component's own ``test_<name>.py``.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from conftest import REPO_ROOT, example_app_paths, launch_example_app

_APPS = example_app_paths()

# Guard against a broken discovery glob silently collecting zero apps (which would
# make the smoke suite "pass" by testing nothing). There are ~473 example apps today
# (~395 under components/, ~78 under layouts/); any regression that drops us below
# 400 should fail loudly at collection time.
assert len(_APPS) > 400, (
    f"Expected >400 example apps, found {len(_APPS)}. "
    "Discovery in example_app_paths() may be broken."
)

# App id (path relative to the repo root) -> stderr substrings to tolerate for that
# app (e.g. a known deprecation an example intentionally still demonstrates).
# Deprecations are otherwise treated as errors.
#
# great_tables.shiny builds render_gt on py-shiny's legacy output_transformer(),
# which emits a ShinyDeprecationWarning when the renderer is constructed. The
# warning comes from the great-tables package, not from the example code, so it
# cannot be fixed here; drop these entries once great-tables moves to
# shiny.render.renderer.Renderer.
# Upstream: https://github.com/posit-dev/great-tables/issues/59 shipped the
# original shiny integration; the transformer migration is still outstanding.
_GREAT_TABLES_DEPRECATION = [
    "ShinyDeprecationWarning: `shiny.render.transformer.output_transformer()`",
    "super().__init__(",
]
ALLOW_STDERR: dict[str, list[str]] = {
    f"components/outputs/table-great-tables/{app}": _GREAT_TABLES_DEPRECATION
    for app in (
        "app-core.py",
        "app-detail-preview.py",
        "app-express.py",
        "app-variation-reactive-core.py",
        "app-variation-reactive-express.py",
        "app-variation-reactive-preview.py",
        "app-variation-styling-core.py",
        "app-variation-styling-express.py",
        "app-variation-styling-preview.py",
    )
}


@pytest.mark.parametrize(
    "app_path",
    [pytest.param(p, id=str(p.relative_to(REPO_ROOT))) for p in _APPS],
)
def test_example_app_smoke(page: Page, app_path: Path, smoke_test) -> None:
    rel = str(app_path.relative_to(REPO_ROOT))
    with launch_example_app(app_path) as app:
        smoke_test(page, app, allow_stderr=ALLOW_STDERR.get(rel, ()))
