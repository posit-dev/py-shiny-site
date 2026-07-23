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

# Guard against a broken discovery glob silently collecting zero apps (which would
# make the smoke suite "pass" by testing nothing). There are ~308 example apps today;
# any regression that drops us below 300 should fail loudly at collection time.
assert len(_APPS) > 300, (
    f"Expected >300 example apps under components/, found {len(_APPS)}. "
    "Discovery in example_app_paths() may be broken."
)

# Temporary opt-outs for apps that use shiny APIs newer than the pinned py-shiny
# submodule. Remove these once the submodule is bumped. Tracked by:
#   https://github.com/posit-dev/py-shiny-site/issues/397
_ISSUE = "posit-dev/py-shiny-site#397"

# App id -> stderr substrings to tolerate (e.g. a known deprecation the example
# still uses). Deprecations are otherwise treated as errors.
ALLOW_STDERR: dict[str, list[str]] = {
    "display-messages/chat/app-preview.py": [
        "ShinyDeprecationWarning: `Chat(messages=...)` is deprecated",
        "chat = ui.Chat(",
    ],
}

# App id -> reason. These can't even launch against the pinned shiny.
XFAIL: dict[str, str] = {
    "outputs/verbatim-text/app-variation-placeholder-rectangle-when-string-is-empty-express.py": (
        f"shiny.express.ui.output_text_verbatim missing in pinned shiny ({_ISSUE})"
    ),
}


def _param(app_path: Path):
    rel = str(app_path.relative_to(_COMPONENTS))
    marks = [pytest.mark.xfail(reason=XFAIL[rel], strict=True)] if rel in XFAIL else []
    return pytest.param(app_path, id=rel, marks=marks)


@pytest.mark.parametrize("app_path", [_param(p) for p in _APPS])
def test_example_app_smoke(page: Page, app_path: Path, smoke_test) -> None:
    rel = str(app_path.relative_to(_COMPONENTS))
    with launch_example_app(app_path) as app:
        smoke_test(page, app, allow_stderr=ALLOW_STDERR.get(rel, ()))
