"""Unit tests for scripts/site_links.py, the internal-link checker.

Not collected by the test-components-* targets (pytest.ini scopes testpaths to
components/). Run explicitly:

    make test-site-links-checker
"""

from __future__ import annotations

from pathlib import Path

import pytest

# pytest's default "prepend" import mode puts scripts/ on sys.path (no
# __init__.py here), so the checker imports as a plain module.
import site_links


@pytest.fixture
def site(tmp_path: Path) -> Path:
    """A minimal rendered site: sub/page.html linking at real/index.html."""
    (tmp_path / "sub").mkdir()
    (tmp_path / "real").mkdir()
    (tmp_path / "real" / "index.html").write_text('<h2 id="known">k</h2>')
    return tmp_path


def findings(root: Path, *, anchors: bool = True) -> set[tuple[str, str]]:
    found, _pages = site_links.check(str(root), check_anchors=anchors)
    return {(f.kind, f.target) for f in found}


def write_page(site: Path, body: str) -> None:
    (site / "sub" / "page.html").write_text(body)


@pytest.mark.parametrize(
    "href",
    [
        "../real/",  # directory with an index.html
        "../real/index.html",  # direct file
        "/real/",  # root-absolute, resolved against the render dir
        "../real/index.html#known",  # anchor that exists
    ],
)
def test_resolvable_links_are_not_reported(site: Path, href: str) -> None:
    write_page(site, f'<a href="{href}">x</a>')
    assert findings(site) == set()


@pytest.mark.parametrize(
    "href",
    [
        "https://example.com/x",  # external
        "//cdn.example.com/x.js",  # protocol-relative
        "mailto:a@b.c",
        "#local",  # same-page fragment
        "${href}",  # JS template literal
        "<%= app.shinylive %>",  # EJS placeholder
        "../site_libs/bootstrap/x.min.css",  # merge-owned hashed asset
        "",
    ],
)
def test_non_site_links_are_skipped(site: Path, href: str) -> None:
    write_page(site, f'<a href="{href}">x</a>')
    assert findings(site) == set()


@pytest.mark.parametrize(
    "wrapper",
    ["<pre>{}</pre>", "<code>{}</code>", "<script>{}</script>"],
)
def test_code_and_script_regions_are_ignored(site: Path, wrapper: str) -> None:
    """Samples name files like `my-styles.css` that are not meant to resolve."""
    write_page(site, wrapper.format('<a href="my-styles.css">x</a>'))
    assert findings(site) == set()


def test_missing_target_is_reported(site: Path) -> None:
    write_page(site, '<a href="../gone.html">x</a>')
    assert findings(site) == {("missing-target", "../gone.html")}


def test_relative_link_missing_leading_slash_is_reported(site: Path) -> None:
    """The py-shiny-site #59 follow-up bug: `templates/x/` instead of `/templates/x/`."""
    write_page(site, '<a href="real/">x</a>')
    assert findings(site) == {("missing-target", "real/")}


def test_directory_without_index_is_reported(site: Path) -> None:
    (site / "empty").mkdir()
    write_page(site, '<a href="../empty/">x</a>')
    assert findings(site) == {("missing-target", "../empty/")}


def test_unrewritten_qmd_is_reported_even_when_the_file_exists(site: Path) -> None:
    """Quarto copies some unresolved .qmd files through; the link is still wrong."""
    (site / "real" / "index.qmd").write_text("source")
    write_page(site, '<a href="../real/index.qmd">x</a>')
    assert findings(site) == {("unrewritten-qmd", "../real/index.qmd")}


def test_missing_anchor_is_reported(site: Path) -> None:
    write_page(site, '<a href="../real/index.html#nope">x</a>')
    assert findings(site) == {("missing-anchor", "../real/index.html#nope")}


def test_anchor_checking_is_off_by_default_in_main(site: Path) -> None:
    """quartodoc omits the ids its own interlinks target; gating on anchors
    would report ~1500 findings from generated api/** pages."""
    write_page(site, '<a href="../real/index.html#nope">x</a>')
    assert site_links.main(["--dir", str(site)]) == 0
    assert site_links.main(["--dir", str(site), "--anchors"]) == 1


def test_name_attribute_counts_as_an_anchor(site: Path) -> None:
    (site / "real" / "index.html").write_text('<a name="legacy"></a>')
    write_page(site, '<a href="../real/index.html#legacy">x</a>')
    assert findings(site) == set()


def test_percent_encoded_paths_resolve(site: Path) -> None:
    (site / "real" / "a b.html").write_text("x")
    write_page(site, '<a href="../real/a%20b.html">x</a>')
    assert findings(site) == set()


def test_query_string_is_stripped_before_resolving(site: Path) -> None:
    write_page(site, '<a href="../real/index.html?v=1">x</a>')
    assert findings(site) == set()


def test_src_attributes_are_checked(site: Path) -> None:
    write_page(site, '<img src="../missing.png">')
    assert findings(site) == {("missing-target", "../missing.png")}


def test_allowlist_suppresses_by_kind_and_target(tmp_path: Path) -> None:
    allow = tmp_path / "allow.txt"
    allow.write_text(
        "# a leading-hash comment\nmissing-target\t../gone.html\n\n"
        # A mid-line '#' is a URL fragment, not a comment.
        "missing-anchor\t../real/index.html#nope\n"
    )
    entries = site_links.load_allowlist(str(allow))
    assert entries == {
        "missing-target\t../gone.html",
        "missing-anchor\t../real/index.html#nope",
    }


def test_main_exits_2_when_the_render_dir_is_absent(tmp_path: Path) -> None:
    assert site_links.main(["--dir", str(tmp_path / "nope")]) == 2


def test_main_exits_0_on_a_clean_site(site: Path) -> None:
    write_page(site, '<a href="../real/">x</a>')
    assert site_links.main(["--dir", str(site)]) == 0


def test_main_exits_1_when_findings_remain(site: Path) -> None:
    write_page(site, '<a href="../gone.html">x</a>')
    assert site_links.main(["--dir", str(site)]) == 1
