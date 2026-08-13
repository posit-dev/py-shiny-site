"""Unit tests for scripts/api_anchors.py, the generated-api anchor fixup.

Not collected by the test-components-* targets (pytest.ini scopes testpaths to
components/). Run explicitly:

    make test-api-anchors
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# pytest's default "prepend" import mode puts scripts/ on sys.path (no
# __init__.py here), so the module imports as a plain module.
import api_anchors

TITLE_BLOCK = '<header id="title-block-header" class="quarto-title-block default">'


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A source tree and a build dir sharing the api/core/ layout."""
    (tmp_path / "api" / "core").mkdir(parents=True)
    (tmp_path / "_build" / "api" / "core").mkdir(parents=True)
    return tmp_path


def write_page(tree: Path, stem: str, *, qmd: str, html: str) -> Path:
    (tree / "api" / "core" / f"{stem}.qmd").write_text(qmd)
    path = tree / "_build" / "api" / "core" / f"{stem}.html"
    path.write_text(html)
    return path


def write_inventory(tree: Path, uris: list[str]) -> Path:
    path = tree / "objects.json"
    path.write_text(json.dumps({"items": [{"name": u, "uri": u} for u in uris]}))
    return path


def run(tree: Path, inventory: Path | None = None) -> api_anchors.Report:
    return api_anchors.ensure_api_anchors(
        str(tree / "_build"),
        source_dir=str(tree),
        inventory_path=str(inventory) if inventory else None,
    )


def test_own_heading_anchor_goes_on_the_title_block(tree: Path) -> None:
    """The id Quarto swallowed off the first heading is restored."""
    page = write_page(
        tree,
        "App",
        qmd="# App { #shiny.App }\n\nbody\n",
        html=f"<html>{TITLE_BLOCK}<h1>App</h1></header></html>",
    )

    report = run(tree)

    assert '<span id="shiny.App"></span>' in page.read_text()
    assert page.read_text().index('id="shiny.App"') > page.read_text().index(
        'id="title-block-header"'
    )
    assert report.by_rule == {"own-heading": 1}


def test_existing_anchor_is_left_alone(tree: Path) -> None:
    """A page whose object id survived rendering is not touched."""
    page = write_page(
        tree,
        "App",
        qmd="# App { #shiny.App }\n",
        html=f'<html>{TITLE_BLOCK}</header><section id="shiny.App">x</section></html>',
    )
    before = page.read_text()

    report = run(tree)

    assert page.read_text() == before
    assert report.anchors_added == 0


def test_rerunning_adds_nothing(tree: Path) -> None:
    """Idempotent: post-render may run over an already-processed build."""
    page = write_page(
        tree,
        "App",
        qmd="# App { #shiny.App }\n",
        html=f"<html>{TITLE_BLOCK}</header></html>",
    )

    run(tree)
    once = page.read_text()
    second = run(tree)

    assert page.read_text() == once
    assert second.anchors_added == 0


def test_heading_without_an_explicit_id_is_not_invented(tree: Path) -> None:
    """A bare `# Exception types` page gets no made-up `shiny.ExceptionTypes`."""
    page = write_page(
        tree,
        "ExceptionTypes",
        qmd="# Exception types\n\nbody\n",
        html=f"<html>{TITLE_BLOCK}</header></html>",
    )

    report = run(tree)

    assert "shiny.ExceptionTypes" not in page.read_text()
    assert report.anchors_added == 0


def test_primary_object_comes_from_the_inventory(tree: Path) -> None:
    """api/core/Session.qmd has no heading id, so the inventory supplies it."""
    page = write_page(
        tree,
        "Session",
        qmd="# Session\n\nTools for managing user sessions.\n",
        html=f"<html>{TITLE_BLOCK}</header></html>",
    )
    inventory = write_inventory(tree, ["api/core/Session.html#shiny.Session"])

    report = run(tree, inventory)

    assert '<span id="shiny.Session"></span>' in page.read_text()
    assert report.by_rule == {"primary-object": 1}


def test_alias_attaches_to_the_canonical_heading(tree: Path) -> None:
    """`shiny.Session.close` lands on the `shiny.session.Session.close` heading."""
    page = write_page(
        tree,
        "Session",
        qmd="# Session\n",
        html=(
            f"<html>{TITLE_BLOCK}</header>"
            '<section id="shiny.session.Session.close">close</section></html>'
        ),
    )
    inventory = write_inventory(tree, ["api/core/Session.html#shiny.Session.close"])

    report = run(tree, inventory)

    html = page.read_text()
    assert '<span id="shiny.Session.close"></span><section' in html
    assert report.by_rule == {"alias": 1}


def test_ambiguous_alias_is_left_unresolved(tree: Path) -> None:
    """Two candidates sharing a tail means no anchor rather than a guess."""
    page = write_page(
        tree,
        "Session",
        qmd="# Session\n",
        html=(
            f"<html>{TITLE_BLOCK}</header>"
            '<section id="shiny.a.Session.close">a</section>'
            '<section id="shiny.b.Session.close">b</section></html>'
        ),
    )
    inventory = write_inventory(tree, ["api/core/Session.html#shiny.Session.close"])

    report = run(tree, inventory)

    assert 'id="shiny.Session.close"' not in page.read_text()
    assert report.unresolved == [("api/core/Session.html", "shiny.Session.close")]


def test_promised_anchor_with_no_target_is_reported_not_faked(tree: Path) -> None:
    """An undocumented member stays broken so the link checker still flags it."""
    page = write_page(
        tree,
        "App",
        qmd="# App { #shiny.App }\n",
        html=f"<html>{TITLE_BLOCK}</header></html>",
    )
    inventory = write_inventory(tree, ["api/core/App.html#shiny.App.lib_prefix"])

    report = run(tree, inventory)

    assert "lib_prefix" not in page.read_text()
    assert report.unresolved == [("api/core/App.html", "shiny.App.lib_prefix")]


def test_multiple_anchors_on_one_page_all_land(tree: Path) -> None:
    """Back-to-front insertion keeps offsets valid across several edits."""
    page = write_page(
        tree,
        "Session",
        qmd="# Session\n",
        html=(
            f"<html>{TITLE_BLOCK}</header>"
            '<section id="shiny.session.Session.close">close</section>'
            '<section id="shiny.session.Session.on_flush">flush</section></html>'
        ),
    )
    inventory = write_inventory(
        tree,
        [
            "api/core/Session.html#shiny.Session",
            "api/core/Session.html#shiny.Session.close",
            "api/core/Session.html#shiny.Session.on_flush",
        ],
    )

    run(tree, inventory)

    html = page.read_text()
    assert '<span id="shiny.Session.close"></span><section id="shiny.session.Session.close"' in html
    assert (
        '<span id="shiny.Session.on_flush"></span><section id="shiny.session.Session.on_flush"'
        in html
    )
    assert f'{TITLE_BLOCK}<span id="shiny.Session"></span>' in html


def test_pages_absent_from_a_shard_are_skipped(tree: Path) -> None:
    """Each shard renders a slice; the inventory covers the whole site."""
    inventory = write_inventory(tree, ["api/core/Missing.html#shiny.Missing"])

    report = run(tree, inventory)

    assert report.anchors_added == 0
    assert report.unresolved == []


def test_page_without_a_title_block_is_reported(tree: Path) -> None:
    """No title block means nowhere safe to put the page's own anchor."""
    write_page(tree, "App", qmd="# App { #shiny.App }\n", html="<html><h1>App</h1></html>")

    report = run(tree)

    assert report.unresolved == [("api/core/App.html", "shiny.App")]
