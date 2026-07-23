"""Verify every component page ships at least one runnable example app.

Each component page lives at ``components/<section>/<name>/index.qmd`` and must
have at least one ``app.py`` / ``app-*.py`` alongside it (which the smoke sweep
in ``test_examples_smoke.py`` then launches). A page with no example app is a
documentation gap and fails here -- unless it is explicitly opted out via
``NO_APP_ALLOWLIST`` below.

This is a static filesystem check (no browser), so it runs under ``make test-apps``.
"""

from pathlib import Path

import pytest

COMPONENTS_DIR = Path(__file__).parent
SECTIONS = ("inputs", "outputs", "display-messages", "layout")

# Component pages allowed to ship WITHOUT a runnable example app. Add a page's
# "<section>/<name>" path here, with a comment explaining why, to opt it out.
NO_APP_ALLOWLIST: set[str] = set()


def _component_pages() -> list[Path]:
    """Every component page directory (one holding a leaf ``index.qmd``)."""
    pages: list[Path] = []
    for section in SECTIONS:
        pages += [p.parent for p in (COMPONENTS_DIR / section).glob("*/index.qmd")]
    return sorted(pages)


_PAGES = _component_pages()

# Guard against a broken glob silently discovering nothing (which would make the
# check vacuously pass). There are ~41 component pages today.
assert len(_PAGES) > 30, (
    f"Expected >30 component pages under components/, found {len(_PAGES)}. "
    "Discovery in _component_pages() may be broken."
)


def _has_example_app(page_dir: Path) -> bool:
    return any(page_dir.glob("app.py")) or any(page_dir.glob("app-*.py"))


def test_no_app_allowlist_entries_are_real() -> None:
    """Keep the opt-out list honest: every entry must name a discovered page."""
    known = {str(p.relative_to(COMPONENTS_DIR)) for p in _PAGES}
    unknown = NO_APP_ALLOWLIST - known
    assert not unknown, (
        f"NO_APP_ALLOWLIST names pages that don't exist (stale/typo): {sorted(unknown)}"
    )


@pytest.mark.parametrize(
    "page_dir",
    _PAGES,
    ids=[str(p.relative_to(COMPONENTS_DIR)) for p in _PAGES],
)
def test_component_page_has_example_app(page_dir: Path) -> None:
    rel = str(page_dir.relative_to(COMPONENTS_DIR))
    if rel in NO_APP_ALLOWLIST:
        pytest.skip(f"{rel} is opted out via NO_APP_ALLOWLIST")
    assert _has_example_app(page_dir), (
        f"Component page '{rel}' has no example app (app.py / app-*.py). "
        f"Add an example app, or opt out by adding '{rel}' to NO_APP_ALLOWLIST "
        "in components/test_component_pages.py (with a reason)."
    )
