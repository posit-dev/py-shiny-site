import sys
from pathlib import Path

# Add scripts/ to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_llms_txt import (
    Page,
    Section,
    SidebarEntry,
    Subsection,
    build_site_structure,
    clean_qmd_content,
    clean_section_name,
    extract_title,
    file_path_to_url,
    generate_llms_full_txt,
    generate_llms_txt,
    walk_sidebar,
)


def test_removes_yaml_frontmatter():
    content = "---\ntitle: Hello\nformat: html\n---\n\nBody text here."
    result = clean_qmd_content(content)
    assert "title: Hello" not in result
    assert "Body text here." in result


def test_removes_quarto_div_fences():
    content = "Before\n:::{.grid}\nInside\n:::\nAfter"
    result = clean_qmd_content(content)
    assert ":::" not in result
    assert "Before" in result
    assert "Inside" in result
    assert "After" in result


def test_removes_multi_colon_fences():
    content = "Before\n::::{.column-screen}\nInside\n::::\nAfter"
    result = clean_qmd_content(content)
    assert "::::" not in result
    assert "Inside" in result


def test_removes_raw_html_blocks():
    content = 'Before\n```{=html}\n<div class="foo">bar</div>\n```\nAfter'
    result = clean_qmd_content(content)
    assert "<div" not in result
    assert "Before" in result
    assert "After" in result


def test_removes_inline_html_tags():
    content = '<span class="emoji">X</span> Hello <div>world</div>'
    result = clean_qmd_content(content)
    assert "<span" not in result
    assert "<div" not in result
    assert "Hello" in result
    assert "world" in result


def test_converts_quarto_code_blocks():
    content = "```{python}\nprint('hi')\n```"
    result = clean_qmd_content(content)
    assert "```python" in result
    assert "{python}" not in result


def test_converts_shinylive_code_blocks():
    content = "```{shinylive-python}\n#| standalone: true\nprint('hi')\n```"
    result = clean_qmd_content(content)
    assert "```python" in result
    assert "shinylive" not in result


def test_preserves_plain_code_blocks():
    content = "```bash\necho hello\n```"
    result = clean_qmd_content(content)
    assert "```bash" in result
    assert "echo hello" in result


def test_preserves_markdown_headings():
    content = "---\ntitle: T\n---\n\n## Section\n\nText here."
    result = clean_qmd_content(content)
    assert "## Section" in result


def test_preserves_links():
    content = "See [this page](https://example.com) for details."
    result = clean_qmd_content(content)
    assert "[this page](https://example.com)" in result


def test_collapses_excessive_blank_lines():
    content = "Line 1\n\n\n\n\nLine 2"
    result = clean_qmd_content(content)
    assert result.count("\n\n\n") == 0
    assert "Line 1\n\nLine 2" in result


def test_removes_shinylive_metadata_comments():
    content = "```python\n#| standalone: true\n#| components: [editor, viewer]\nprint('hi')\n```"
    result = clean_qmd_content(content)
    assert "#| standalone" not in result
    assert "print('hi')" in result


# --- Tests for clean_section_name ---


def test_clean_section_name_image_and_bold():
    assert clean_section_name("![](/images/sliders.svg){.sidebar-icon .sidebar-subtitle}__Inputs__") == "Inputs"


def test_clean_section_name_emoji_span_and_bold():
    assert clean_section_name("<span class='emoji-icon'>🤖</span> __Generative AI__") == "Generative AI"


def test_clean_section_name_plain_text():
    assert clean_section_name("Deploy") == "Deploy"


def test_clean_section_name_image_title_no_bold():
    assert clean_section_name("![](/images/blank-pixel.png){.sidebar-title}__COMPONENTS__") == "COMPONENTS"


# --- Tests for extract_title ---


def test_extract_title_from_title():
    assert extract_title("---\ntitle: Foundations\nformat: html\n---\n\nBody") == "Foundations"


def test_extract_title_from_pagetitle():
    assert extract_title('---\npagetitle: "Shiny for Python"\n---\n\nBody') == "Shiny for Python"


def test_extract_title_pagetitle_preferred():
    assert extract_title('---\npagetitle: "Page Title"\ntitle: Regular Title\n---\n\nBody') == "Page Title"


def test_extract_title_missing():
    assert extract_title("---\nformat: html\n---\n\nBody") is None


# --- Tests for walk_sidebar ---


def test_walk_plain_string_entries():
    entries = list(walk_sidebar(["get-started/index.qmd", "get-started/install.qmd"]))
    assert entries == [SidebarEntry(None, "get-started/index.qmd"), SidebarEntry(None, "get-started/install.qmd")]


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
    entries = list(walk_sidebar([{"section": "Deploy", "contents": [{"text": "Overview", "href": "deploy.qmd"}, "cloud.qmd"]}]))
    assert entries == [SidebarEntry("Deploy", "deploy.qmd"), SidebarEntry("Deploy", "cloud.qmd")]


# --- Tests for file_path_to_url ---

BASE_URL = "https://shiny.posit.co/py/"


def test_url_qmd_to_html():
    assert file_path_to_url("docs/overview.qmd", BASE_URL) == "https://shiny.posit.co/py/docs/overview.html"


def test_url_index_qmd_to_trailing_slash():
    assert file_path_to_url("get-started/index.qmd", BASE_URL) == "https://shiny.posit.co/py/get-started/"


def test_url_component_dir_index():
    assert file_path_to_url("components/inputs/checkbox/index.qmd", BASE_URL) == "https://shiny.posit.co/py/components/inputs/checkbox/"


def test_url_strips_leading_slash():
    assert file_path_to_url("/layouts/index.qmd", BASE_URL) == "https://shiny.posit.co/py/layouts/"


def test_url_html_passthrough():
    assert file_path_to_url("layouts/navbars/index.html", BASE_URL) == "https://shiny.posit.co/py/layouts/navbars/"


# --- Tests for build_site_structure ---


def test_build_site_structure_returns_sections(tmp_path):
    """Test with a minimal _quarto.yml and .qmd files."""
    quarto_yml = tmp_path / "_quarto.yml"
    quarto_yml.write_text(
        """
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
"""
    )
    (tmp_path / "get-started").mkdir()
    (tmp_path / "get-started" / "index.qmd").write_text(
        "---\ntitle: Get Started\n---\nWelcome."
    )
    (tmp_path / "get-started" / "install.qmd").write_text(
        "---\ntitle: Install\n---\nInstall instructions."
    )
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "overview.qmd").write_text(
        "---\ntitle: Overview\n---\nOverview content."
    )

    sections = build_site_structure(tmp_path)
    assert len(sections) >= 2

    # First section is "Get Started" (from sidebar id)
    gs = sections[0]
    assert gs.name == "Get Started"
    assert len(gs.pages) == 2
    assert gs.pages[0].title == "Get Started"
    assert gs.pages[1].title == "Install"

    # Second section is "Concepts" (from sidebar id)
    concepts = sections[1]
    assert concepts.name == "Concepts"
    assert concepts.subsections[0].name == "Essentials"
    assert concepts.subsections[0].pages[0].title == "Overview"


def test_build_site_structure_discovers_templates(tmp_path):
    """Templates are found by directory scan, not sidebar."""
    quarto_yml = tmp_path / "_quarto.yml"
    quarto_yml.write_text("website:\n  sidebar: []\n")
    (tmp_path / "templates" / "basic-app").mkdir(parents=True)
    (tmp_path / "templates" / "basic-app" / "index.qmd").write_text(
        "---\ntitle: Basic App\n---\nA basic app."
    )
    (tmp_path / "templates" / "dashboard").mkdir(parents=True)
    (tmp_path / "templates" / "dashboard" / "index.qmd").write_text(
        "---\ntitle: Dashboard\n---\nA dashboard."
    )

    sections = build_site_structure(tmp_path)
    templates = [s for s in sections if s.name == "Templates"]
    assert len(templates) == 1
    assert len(templates[0].pages) == 2
    # Alphabetical order
    assert templates[0].pages[0].title == "Basic App"
    assert templates[0].pages[1].title == "Dashboard"


def test_build_site_structure_resolves_fragment_hrefs(tmp_path):
    """Sidebar entries with # in href should resolve to the parent page (deduplicated)."""
    quarto_yml = tmp_path / "_quarto.yml"
    quarto_yml.write_text(
        """
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
"""
    )
    (tmp_path / "layouts").mkdir()
    (tmp_path / "layouts" / "index.qmd").write_text(
        "---\ntitle: Layouts\n---\nLayout docs."
    )
    (tmp_path / "layouts" / "navbars").mkdir()
    (tmp_path / "layouts" / "navbars" / "index.qmd").write_text(
        "---\ntitle: Navbars\n---\nNavbar docs."
    )
    sections = build_site_structure(tmp_path)
    layouts = [s for s in sections if s.name == "Layouts"]
    assert len(layouts) == 1
    # The layouts index page plus the navbars page (deduplicated from two fragment hrefs)
    total_pages = len(layouts[0].pages)
    for sub in layouts[0].subsections:
        total_pages += len(sub.pages)
    assert total_pages == 2


# --- Tests for generate_llms_txt and generate_llms_full_txt ---


def _make_test_sections():
    return [
        Section(
            name="Get Started",
            pages=[Page(title="Install", file_path="get-started/install.qmd", content="---\ntitle: Install\n---\n\nInstall Shiny with pip.")],
            subsections=[],
        ),
        Section(
            name="Components",
            pages=[],
            subsections=[
                Subsection(name="Inputs", pages=[
                    Page(title="Checkbox", file_path="components/inputs/checkbox/index.qmd", content="---\ntitle: Checkbox\n---\n\nA checkbox input."),
                ]),
            ],
        ),
    ]


def test_generate_llms_txt_format():
    sections = _make_test_sections()
    output = generate_llms_txt(sections)
    assert output.startswith("# Shiny for Python\n")
    assert "> " in output
    assert "## Get Started" in output
    assert "- [Install](https://shiny.posit.co/py/get-started/install.html)" in output
    assert "## Components" in output
    assert "### Inputs" in output
    assert "- [Checkbox](https://shiny.posit.co/py/components/inputs/checkbox/)" in output


def test_generate_llms_txt_no_content():
    sections = _make_test_sections()
    output = generate_llms_txt(sections)
    assert "Install Shiny with pip" not in output
    assert "A checkbox input" not in output


def test_generate_llms_full_txt_format():
    sections = _make_test_sections()
    output = generate_llms_full_txt(sections)
    assert output.startswith("# Shiny for Python\n")
    assert "## Get Started" in output
    assert "### Install" in output
    assert "Install Shiny with pip." in output
    assert "---" in output
    assert "## Components" in output
    assert "### Inputs" in output
    assert "#### Checkbox" in output
    assert "A checkbox input." in output


def test_generate_llms_full_txt_cleans_content():
    sections = [Section(name="Test", pages=[
        Page(title="Page", file_path="test/page.qmd", content="---\ntitle: Page\n---\n\n:::{.grid}\nClean text.\n:::\n"),
    ], subsections=[])]
    output = generate_llms_full_txt(sections)
    assert "title: Page" not in output
    assert ":::" not in output
    assert "Clean text." in output
