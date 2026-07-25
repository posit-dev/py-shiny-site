"""Verify component pages ship at least one runnable example app.

Each component page lives at ``components/<section>/<name>/index.qmd`` and should
have at least one ``app.py`` / ``app-*.py`` alongside it (which the smoke sweep
in ``test_examples_smoke.py`` then launches). A page with no example app is a
documentation gap.

Every discovered page is enforced. A page may only skip the requirement by
being listed in ``EXEMPT_PAGES`` with a documented reason -- the set should
normally stay empty.

This is a static filesystem check (no browser), so it runs under ``make test-apps``.
"""

from pathlib import Path

import pytest

COMPONENTS_DIR = Path(__file__).parent
SECTIONS = ("inputs", "outputs", "display-messages", "layout")

# Component pages ("<section>/<name>") exempt from the example-app requirement.
# Keep this empty; add an entry only with a comment explaining why the page
# cannot ship a runnable example app.
EXEMPT_PAGES: set[str] = set()


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


def test_exempt_pages_are_real() -> None:
    """Keep the exempt list honest: every entry must name a discovered page."""
    known = {str(p.relative_to(COMPONENTS_DIR)) for p in _PAGES}
    unknown = EXEMPT_PAGES - known
    assert not unknown, (
        f"EXEMPT_PAGES names pages that don't exist (stale/typo): {sorted(unknown)}"
    )


@pytest.mark.parametrize(
    "page_dir",
    _PAGES,
    ids=[str(p.relative_to(COMPONENTS_DIR)) for p in _PAGES],
)
def test_component_page_has_example_app(page_dir: Path) -> None:
    rel = str(page_dir.relative_to(COMPONENTS_DIR))
    if rel in EXEMPT_PAGES:
        pytest.skip(f"{rel} is exempt (see EXEMPT_PAGES)")
    assert _has_example_app(page_dir), (
        f"Component page '{rel}' has no example app (app.py / app-*.py). "
        "Add an example app for it."
    )
