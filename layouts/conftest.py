"""Shared pytest fixtures and helpers for layouts example-app tests.

The shared helpers live in ``components/conftest.py`` (the single source of
truth). This module re-exports them so that ``from conftest import ...`` keeps
working in every test file no matter which ``conftest`` module Python finds
first on ``sys.path`` now that two such modules exist (``components/`` and
``layouts/``). It also registers the same fixtures (``connect_options``,
``smoke_test``) for the ``layouts/`` subtree, so CI's remote Playwright server
is used here too.

Only the public ``shiny`` package API is used:
``shiny.pytest.create_app_fixture``, ``shiny.playwright.controller`` and
``shiny.run.ShinyAppProc``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_COMPONENTS_CONFTEST = Path(__file__).parent.parent / "components" / "conftest.py"

_spec = importlib.util.spec_from_file_location(
    "py_shiny_site_components_conftest", _COMPONENTS_CONFTEST
)
assert _spec is not None and _spec.loader is not None
_components = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_components)

# Re-export every helper that tests import directly. This includes the
# underscore helpers (components/test_conftest.py imports them) and the
# smoke-sweep helpers (components/test_examples_smoke.py imports them):
# whichever conftest wins the `import conftest` race has them all.
create_example_fixture = _components.create_example_fixture
split_shinylive_app = _components.split_shinylive_app
example_app_paths = _components.example_app_paths
launch_example_app = _components.launch_example_app
smoke_test = _components.smoke_test
connect_options = _components.connect_options
_num_file_sections = _components._num_file_sections
FILE_MARKER = _components.FILE_MARKER
COMPONENTS_DIR = _components.COMPONENTS_DIR
REPO_ROOT = _components.REPO_ROOT
EXAMPLE_APP_DIRS = _components.EXAMPLE_APP_DIRS

LAYOUTS_DIR = Path(__file__).parent
