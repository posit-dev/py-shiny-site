"""Tests for scripts/generate_llms_txt.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_llms_txt import (
    Page,
    Section,
    SidebarEntry,
    Subsection,
    _load_page,
    build_site_structure,
    clean_section_name,
    file_path_to_url,
    generate_llms_full_txt,
    post_process_llms_md,
    walk_sidebar,
)


# ---------------------------------------------------------------------------
# post_process_llms_md
# ---------------------------------------------------------------------------


def test_strips_quarto_directive_lines():
    content = "```python\n#| standalone: true\n#| components: [editor, viewer]\nprint('hi')\n```\n"
    result = post_process_llms_md(content)
    assert "#|" not in result
    assert "print('hi')" in result


def test_keeps_code_block_content():
    content = "```python\nmy_func()\n```\n"
    result = post_process_llms_md(content)
    assert "my_func()" in result
    assert "```python" in result


def test_normalizes_numberSource_to_python():
    # Quarto renders fences both with and without a space before the language tag.
    for fence in ("```numberSource", "``` numberSource"):
        result = post_process_llms_md(f"{fence}\ncode()\n```\n")
        assert "```python" in result
        assert "numberSource" not in result


def test_normalizes_shinylive_python_to_python():
    content = "```shinylive-python\nprint('hi')\n```\n"
    result = post_process_llms_md(content)
    assert "```python" in result
    assert "shinylive-python" not in result


def test_strips_blockquoted_directive_lines():
    # #| lines inside blockquoted code blocks (e.g. callout notes) must be stripped.
    content = "> ```python\n> #| standalone: true\n> code()\n> ```\n"
    result = post_process_llms_md(content)
    assert "#|" not in result
    assert "code()" in result


def test_strips_jupyter_double_hash_directives():
    # Jupyter notebooks use ##| instead of #|
    content = "```python\n##| echo: false\ncode()\n```\n"
    result = post_process_llms_md(content)
    assert "##|" not in result
    assert "code()" in result


def test_preserves_multifile_app_marker_inside_code_block():
    # "## file: app.py" inside a code block must not be treated as a heading
    # and must not trigger section-skip logic — it should be preserved as code.
    content = "```python\n## file: app.py\nfrom shiny import App\n```\n"
    result = post_process_llms_md(content)
    assert "## file: app.py" in result
    assert "from shiny import App" in result


def test_strips_relevant_functions_section():
    content = "Intro.\n\n## Relevant Functions\n\n- `foo()`\n- `bar()`\n\n## Details\n\nMore.\n"
    result = post_process_llms_md(content)
    assert "## Relevant Functions" not in result
    assert "foo()" not in result
    assert "## Details" in result
    assert "More." in result


def test_strips_variation_showcase_section():
    content = "Intro.\n\n## Variation Showcase\n\nKitchen sink.\n\n![](thumbnail.png)\n"
    result = post_process_llms_md(content)
    assert "## Variation Showcase" not in result
    assert "Kitchen sink" not in result


def test_keeps_other_sections():
    content = "## Express\n\n```python\ncode()\n```\n\n## Core\n\n```python\ncode()\n```\n"
    result = post_process_llms_md(content)
    assert "## Express" in result
    assert "## Core" in result


def test_strips_bare_external_link_lines():
    # Bare external links (navigation, shinylive showcases) are stripped.
    for url in ("https://shinylive.io/py/editor/#h=0&code=abc", "https://github.com/posit-dev/app"):
        content = f"Prose.\n\n[ View App]({url})\n"
        result = post_process_llms_md(content)
        assert url not in result
        assert "Prose." in result


def test_strips_bare_image_references():
    content = "Text.\n\n![](thumbnail.png)\n\nMore text.\n"
    result = post_process_llms_md(content)
    assert "thumbnail.png" not in result
    assert "More text." in result


def test_collapses_excessive_blank_lines():
    content = "Line 1\n\n\n\n\nLine 2\n"
    result = post_process_llms_md(content)
    assert "\n\n\n" not in result
    assert "Line 1" in result
    assert "Line 2" in result


def test_empty_content():
    assert post_process_llms_md("") == "\n"
    assert post_process_llms_md("\n\n") == "\n"


# ---------------------------------------------------------------------------
# clean_section_name
# ---------------------------------------------------------------------------


def test_clean_section_name():
    assert clean_section_name("![](/images/sliders.svg){.sidebar-icon .sidebar-subtitle}__Inputs__") == "Inputs"
    assert clean_section_name("![](/images/blank-pixel.png){.sidebar-title}__COMPONENTS__") == "COMPONENTS"
    assert clean_section_name("<span class='emoji-icon'>🤖</span> __Generative AI__") == "Generative AI"
    assert clean_section_name("Deploy") == "Deploy"


# ---------------------------------------------------------------------------
# file_path_to_url
# ---------------------------------------------------------------------------


def test_url_qmd_to_html():
    assert file_path_to_url("docs/overview.qmd") == "https://shiny.posit.co/py/docs/overview.html"


def test_url_index_qmd_to_trailing_slash():
    assert file_path_to_url("get-started/index.qmd") == "https://shiny.posit.co/py/get-started/"


def test_url_component_dir_index():
    assert file_path_to_url("components/inputs/checkbox/index.qmd") == "https://shiny.posit.co/py/components/inputs/checkbox/"


def test_url_strips_leading_slash():
    assert file_path_to_url("/layouts/index.qmd") == "https://shiny.posit.co/py/layouts/"


def test_url_html_passthrough():
    assert file_path_to_url("layouts/navbars/index.html") == "https://shiny.posit.co/py/layouts/navbars/"


# ---------------------------------------------------------------------------
# walk_sidebar
# ---------------------------------------------------------------------------


def test_walk_plain_string_entries():
    entries = list(walk_sidebar(["get-started/index.qmd", "get-started/install.qmd"]))
    assert entries == [
        SidebarEntry(None, "get-started/index.qmd"),
        SidebarEntry(None, "get-started/install.qmd"),
    ]


def test_walk_section_with_contents():
    entries = list(walk_sidebar([{"section": "![](/images/sliders.svg){.sidebar-icon}__Inputs__", "contents": ["a.qmd", "b.qmd"]}]))
    assert entries == [SidebarEntry("Inputs", "a.qmd"), SidebarEntry("Inputs", "b.qmd")]


def test_walk_href_entry():
    entries = list(walk_sidebar([{"text": "Overview", "href": "deploy.qmd"}]))
    assert entries == [SidebarEntry(None, "deploy.qmd")]


def test_walk_file_entry():
    entries = list(walk_sidebar([{"text": "Get Started", "file": "index.qmd"}]))
    assert entries == [SidebarEntry(None, "index.qmd")]


def test_walk_resolves_fragment_hrefs():
    entries = list(walk_sidebar([{"text": "X", "href": "/page.html#section"}]))
    assert entries == [SidebarEntry(None, "page.html")]


def test_walk_nested_sections():
    entries = list(walk_sidebar([{
        "section": "Deploy",
        "contents": [{"text": "Overview", "href": "deploy.qmd"}, "cloud.qmd"],
    }]))
    assert entries == [SidebarEntry("Deploy", "deploy.qmd"), SidebarEntry("Deploy", "cloud.qmd")]


def test_walk_deduplicates_entries():
    entries = list(walk_sidebar(["a.qmd", "a.qmd", "b.qmd"]))
    assert len(entries) == 2


# ---------------------------------------------------------------------------
# build_site_structure
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# _load_page — title extraction edge cases
# ---------------------------------------------------------------------------


def test_load_page_extracts_title_from_first_heading(tmp_path):
    build_dir = tmp_path / "_build"
    (build_dir / "docs").mkdir(parents=True)
    (build_dir / "docs" / "overview.llms.md").write_text("# Overview\n\nBody text.\n")
    page = _load_page(build_dir, "docs/overview.qmd")
    assert page.title == "Overview"
    assert "Body text." in page.content
    assert "# Overview" not in page.content


def test_load_page_title_not_extracted_from_python_comment_in_code(tmp_path):
    # A Python comment "# foo" inside a code block must not become the page title.
    build_dir = tmp_path / "_build"
    (build_dir / "docs").mkdir(parents=True)
    (build_dir / "docs" / "page.llms.md").write_text(
        "## Section\n\n```python\n# Create a widget\nwidget()\n```\n"
    )
    page = _load_page(build_dir, "docs/page.qmd")
    assert page.title != "Create a widget"
    assert "widget()" in page.content


def test_load_page_title_found_after_nav_link(tmp_path):
    # Template pages have a nav link on line 1 before the # Title heading.
    build_dir = tmp_path / "_build"
    (build_dir / "templates" / "my-app").mkdir(parents=True)
    (build_dir / "templates" / "my-app" / "index.llms.md").write_text(
        "[ Back to Templates](../../templates/)\n\n# My App Template\n\nDescription.\n"
    )
    page = _load_page(build_dir, "templates/my-app/index.qmd")
    assert page.title == "My App Template"
    assert "Description." in page.content


def test_load_page_returns_none_for_missing_file(tmp_path):
    build_dir = tmp_path / "_build"
    build_dir.mkdir()
    assert _load_page(build_dir, "docs/nonexistent.qmd") is None


# ---------------------------------------------------------------------------
# build_site_structure — section ordering
# ---------------------------------------------------------------------------


def _write_llms(build_dir: Path, rel_path: str, title: str, body: str) -> None:
    """Write a minimal .llms.md file for testing."""
    path = build_dir / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body}")


def test_build_site_structure_returns_sections(tmp_path):
    quarto_yml = tmp_path / "_quarto.yml"
    quarto_yml.write_text("""
website:
  sidebar:
    - id: get-started
      contents:
        - get-started/index.qmd
        - get-started/install.qmd
    - id: concepts
      contents:
        - section: "Essentials"
          contents:
            - docs/overview.qmd
""")
    build = tmp_path / "_build"
    _write_llms(build, "get-started/index.llms.md", "Get Started", "Welcome.")
    _write_llms(build, "get-started/install.llms.md", "Install", "Install instructions.")
    _write_llms(build, "docs/overview.llms.md", "Overview", "Overview content.")

    sections = build_site_structure(tmp_path)
    assert len(sections) >= 2

    gs = sections[0]
    assert gs.name == "Get Started"
    assert len(gs.pages) == 2
    assert gs.pages[0].title == "Get Started"
    assert gs.pages[1].title == "Install"

    concepts = sections[1]
    assert concepts.name == "Concepts"
    assert concepts.subsections[0].name == "Essentials"
    assert concepts.subsections[0].pages[0].title == "Overview"


def test_build_site_structure_skips_missing_llms_files(tmp_path):
    quarto_yml = tmp_path / "_quarto.yml"
    quarto_yml.write_text("""
website:
  sidebar:
    - id: get-started
      contents:
        - get-started/index.qmd
        - get-started/missing.qmd
""")
    build = tmp_path / "_build"
    _write_llms(build, "get-started/index.llms.md", "Get Started", "Welcome.")
    # missing.llms.md intentionally not created

    sections = build_site_structure(tmp_path)
    assert sections[0].pages[0].title == "Get Started"
    assert len(sections[0].pages) == 1  # missing page skipped


def test_build_site_structure_discovers_templates(tmp_path):
    quarto_yml = tmp_path / "_quarto.yml"
    quarto_yml.write_text("website:\n  sidebar: []\n")
    build = tmp_path / "_build"
    _write_llms(build, "templates/basic-app/index.llms.md", "Basic App", "A basic app.")
    _write_llms(build, "templates/dashboard/index.llms.md", "Dashboard", "A dashboard.")

    sections = build_site_structure(tmp_path)
    templates = [s for s in sections if s.name == "Templates"]
    assert len(templates) == 1
    assert len(templates[0].pages) == 2
    assert templates[0].pages[0].title == "Basic App"
    assert templates[0].pages[1].title == "Dashboard"


def test_build_site_structure_section_order(tmp_path):
    # Sections must come out in Get Started → Concepts → Components order
    # regardless of the order sidebars appear in _quarto.yml.
    quarto_yml = tmp_path / "_quarto.yml"
    quarto_yml.write_text("""
website:
  sidebar:
    - id: components
      contents:
        - components/index.qmd
    - id: get-started
      contents:
        - get-started/index.qmd
    - id: concepts
      contents:
        - docs/overview.qmd
""")
    build = tmp_path / "_build"
    _write_llms(build, "components/index.llms.md", "Components", "Components content.")
    _write_llms(build, "get-started/index.llms.md", "Get Started", "Get started content.")
    _write_llms(build, "docs/overview.llms.md", "Overview", "Concepts content.")

    sections = build_site_structure(tmp_path)
    names = [s.name for s in sections]
    assert names.index("Get Started") < names.index("Concepts")
    assert names.index("Concepts") < names.index("Components")


def test_build_site_structure_resolves_fragment_hrefs(tmp_path):
    quarto_yml = tmp_path / "_quarto.yml"
    quarto_yml.write_text("""
website:
  sidebar:
    - id: layouts
      contents:
        - text: "LAYOUTS"
          href: "layouts/index.qmd"
        - section: "Navbars"
          contents:
            - text: "Navbar at Top"
              href: "/layouts/navbars/index.html#navbar-at-top"
            - text: "Navbar at Bottom"
              href: "/layouts/navbars/index.html#navbar-at-bottom"
""")
    build = tmp_path / "_build"
    _write_llms(build, "layouts/index.llms.md", "Layouts", "Layout docs.")
    _write_llms(build, "layouts/navbars/index.llms.md", "Navbars", "Navbar docs.")

    sections = build_site_structure(tmp_path)
    layouts = [s for s in sections if s.name == "Layouts"]
    assert len(layouts) == 1
    total_pages = len(layouts[0].pages) + sum(len(s.pages) for s in layouts[0].subsections)
    assert total_pages == 2  # deduplicated


# ---------------------------------------------------------------------------
# generate_llms_full_txt
# ---------------------------------------------------------------------------


def test_generate_llms_full_txt_format():
    sections = [
        Section(
            name="Get Started",
            pages=[Page(title="Install", file_path="get-started/install.qmd", content="Install Shiny with pip.\n")],
            subsections=[],
        ),
        Section(
            name="Components",
            pages=[],
            subsections=[
                Subsection(name="Inputs", pages=[
                    Page(title="Checkbox", file_path="components/inputs/checkbox/index.qmd", content="A checkbox input.\n"),
                ]),
            ],
        ),
    ]
    output = generate_llms_full_txt(sections)
    assert output.startswith("# Shiny for Python\n")
    assert "## Get Started" in output
    assert "### Install" in output
    assert "Source: https://shiny.posit.co/py/get-started/install.html" in output
    assert "Install Shiny with pip." in output
    assert "---" in output
    assert "## Components" in output
    assert "### Inputs" in output
    assert "#### Checkbox" in output
    assert "Source: https://shiny.posit.co/py/components/inputs/checkbox/" in output
    assert "A checkbox input." in output
