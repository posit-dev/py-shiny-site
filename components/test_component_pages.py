"""Verify component pages ship at least one runnable example app.

Each component page lives at ``components/<section>/<name>/index.qmd`` and should
have at least one ``app.py`` / ``app-*.py`` alongside it (which the smoke sweep
in ``test_examples_smoke.py`` then launches). A page with no example app is a
documentation gap.

For now enforcement is scoped to the pages in ``ENFORCE_HAS_APP`` (just the
accordion page); every other page is discovered but skipped. Broaden coverage by
adding paths here -- or, once all pages qualify, invert to "enforce all except an
allowlist".

This is a static filesystem check (no browser), so it runs under ``make test-apps``.
"""

from pathlib import Path

import pytest

COMPONENTS_DIR = Path(__file__).parent
SECTIONS = ("inputs", "outputs", "display-messages", "layout")

# Component pages ("<section>/<name>") whose example-app coverage is enforced.
ENFORCE_HAS_APP: set[str] = {
    "layout/accordion",
}


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


def test_enforced_pages_are_real() -> None:
    """Keep the enforce list honest: every entry must name a discovered page."""
    known = {str(p.relative_to(COMPONENTS_DIR)) for p in _PAGES}
    unknown = ENFORCE_HAS_APP - known
    assert not unknown, (
        f"ENFORCE_HAS_APP names pages that don't exist (stale/typo): {sorted(unknown)}"
    )


@pytest.mark.parametrize(
    "page_dir",
    _PAGES,
    ids=[str(p.relative_to(COMPONENTS_DIR)) for p in _PAGES],
)
def test_component_page_has_example_app(page_dir: Path) -> None:
    rel = str(page_dir.relative_to(COMPONENTS_DIR))
    if rel not in ENFORCE_HAS_APP:
        pytest.skip(f"{rel} not yet enforced (see ENFORCE_HAS_APP)")
    assert _has_example_app(page_dir), (
        f"Component page '{rel}' has no example app (app.py / app-*.py). "
        "Add an example app for it."
    )
