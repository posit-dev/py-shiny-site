import sys
from pathlib import Path

# Add scripts/ to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_llms_txt import (
    Page,
    Section,
    SidebarEntry,
    Subsection,
    _first_paragraph_with_see_also,
    _is_input_component_page,
    _is_listing_page,
    _parse_frontmatter,
    _resolve_links,
    _strip_html_outside_code,
    build_site_structure,
    clean_qmd_content,
    clean_section_name,
    extract_title,
    file_path_to_url,
    generate_llms_full_txt,
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


def test_converts_shinylive_code_blocks_with_space():
    content = "``` {shinylive-python}\nprint('hi')\n```"
    result = clean_qmd_content(content)
    assert "```python" in result
    assert "{shinylive-python}" not in result


def test_strips_html_comments_multiline():
    content = "Before.\n\n<!--\nThis is commented out.\n-->\n\nAfter."
    result = clean_qmd_content(content)
    assert "Before." in result
    assert "commented out" not in result
    assert "After." in result


def test_strips_html_comments_inline():
    content = "Hello <!-- inline comment --> world."
    result = clean_qmd_content(content)
    assert "Hello" in result
    assert "world" in result
    assert "inline comment" not in result


def test_drops_hidden_code_blocks():
    content = "Before.\n\n```{python}\n#| echo: false\nimport sys\n```\n\nAfter."
    result = clean_qmd_content(content)
    assert "import sys" not in result
    assert "Before." in result
    assert "After." in result


def test_drops_include_false_code_blocks():
    content = "```python\n#| include: false\nsetup_code()\n```\n\nProse."
    result = clean_qmd_content(content)
    assert "setup_code" not in result
    assert "Prose." in result


def test_keeps_visible_code_blocks():
    content = "```python\nmy_app_code()\n```"
    result = clean_qmd_content(content)
    assert "my_app_code()" in result


def test_strips_show_code_label():
    content = "See below.\n\nShow code\n\n```python\nx = 1\n```"
    result = clean_qmd_content(content)
    assert "Show code" not in result
    assert "x = 1" in result


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


# ---------------------------------------------------------------------------
# Fix 1: HTML stripping preserves backtick spans
# ---------------------------------------------------------------------------

def test_strip_html_preserves_inline_code():
    line = "Use `input.<checkbox_id>()` to get the value."
    result = _strip_html_outside_code(line)
    assert "`input.<checkbox_id>()`" in result


def test_strip_html_removes_tags_outside_code():
    line = "See <strong>this</strong> and `keep.<tag>()`."
    result = _strip_html_outside_code(line)
    assert "<strong>" not in result
    assert "this" in result
    assert "`keep.<tag>()`" in result


def test_strip_html_preserves_prose_placeholders():
    line = "where <name> is the function and <checkbox_id> is the id."
    result = _strip_html_outside_code(line)
    assert "<name>" in result
    assert "<checkbox_id>" in result


def test_strip_html_removes_closing_tags():
    line = "Hello </div> world."
    result = _strip_html_outside_code(line)
    assert "</div>" not in result
    assert "Hello" in result and "world" in result


def test_strip_html_removes_tags_with_attributes():
    line = 'See <span class="foo">text</span>.'
    result = _strip_html_outside_code(line)
    assert "<span" not in result
    assert "text" in result


def test_clean_qmd_preserves_input_id_placeholders():
    content = "Use `input.<my_id>()` to access the value."
    result = clean_qmd_content(content)
    assert "`input.<my_id>()`" in result


# ---------------------------------------------------------------------------
# Fix 2: Relative links resolved to absolute URLs
# ---------------------------------------------------------------------------

def test_resolve_links_relative_qmd():
    content = "See [Action Link](../action-link/index.qmd) for more."
    result = _resolve_links(content, "components/inputs/action-button/index.qmd")
    assert "../action-link/index.qmd" not in result
    assert "https://shiny.posit.co/py/components/inputs/action-link/" in result


def test_resolve_links_absolute_path():
    content = "See [API docs](/api/core/ui.navset_hidden.qmd)."
    result = _resolve_links(content, "docs/some-page.qmd")
    assert "/api/core/ui.navset_hidden.qmd" not in result
    assert "https://shiny.posit.co/py/api/core/ui.navset_hidden.html" in result


def test_resolve_links_external_unchanged():
    content = "See [Shiny](https://shiny.posit.co/py/) for details."
    result = _resolve_links(content, "docs/page.qmd")
    assert result == content


def test_clean_qmd_resolves_links():
    content = "---\ntitle: T\n---\nSee [Checkbox](../checkbox/index.qmd)."
    result = clean_qmd_content(content, "components/inputs/action-button/index.qmd")
    assert "../checkbox/index.qmd" not in result
    assert "https://shiny.posit.co/py/components/inputs/checkbox/" in result


# ---------------------------------------------------------------------------
# Fix 3: Template headings stripped
# ---------------------------------------------------------------------------

def test_strips_details_heading():
    content = "## Details\n\nSome content here."
    result = clean_qmd_content(content)
    assert "## Details" not in result
    assert "Some content here." in result


def test_strips_variations_heading():
    content = "## Variations\n\nVariant description."
    result = clean_qmd_content(content)
    assert "## Variations" not in result
    assert "Variant description." in result


def test_preserves_other_headings():
    content = "## Installation\n\n## Details\n\nContent."
    result = clean_qmd_content(content)
    assert "## Installation" in result
    assert "## Details" not in result


# ---------------------------------------------------------------------------
# Fix 4: Listing pages use description only
# ---------------------------------------------------------------------------

def test_is_listing_page_true_with_listing():
    content = "---\ntitle: Components\npagedescription: Inputs and more.\nlisting:\n  - id: input\n---\n\nBody."
    assert _is_listing_page(content) is True


def test_is_listing_page_true_without_listing():
    # Hub pages like layouts/index.qmd have pagedescription but no listing:
    content = "---\ntitle: Shiny Layouts\npagedescription: Layout frameworks.\nsidebar: false\n---\n\nBody."
    assert _is_listing_page(content) is True


def test_is_listing_page_false_no_pagedescription():
    content = "---\ntitle: Action Button\n---\n\nBody."
    assert _is_listing_page(content) is False


def test_is_listing_page_false_listing_without_pagedescription():
    # Component detail pages have listing: for example widgets but no pagedescription
    content = "---\ntitle: Action Button\nlisting:\n- id: example\n---\n\nBody."
    assert _is_listing_page(content) is False


# ---------------------------------------------------------------------------
# Fix 5: Input component pages truncated to first paragraph
# ---------------------------------------------------------------------------

def test_is_input_component_page_true():
    assert _is_input_component_page("components/inputs/checkbox/index.qmd") is True
    assert _is_input_component_page("components/inputs/slider/index.qmd") is True


def test_is_input_component_page_false_for_outputs():
    assert _is_input_component_page("components/outputs/plot-matplotlib/index.qmd") is False


def test_is_input_component_page_false_for_display_messages():
    assert _is_input_component_page("components/display-messages/notifications/index.qmd") is False


def test_first_paragraph_returns_only_first():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    assert _first_paragraph_with_see_also(text) == "First paragraph.\n"


def test_first_paragraph_skips_leading_blank_lines():
    text = "\n\nFirst paragraph.\n\nSecond paragraph."
    assert _first_paragraph_with_see_also(text) == "First paragraph.\n"


def test_first_paragraph_preserves_see_also():
    text = "A checkbox input.\n\nFollow these steps.\n\nSee also: [Checkbox Group](https://example.com/)"
    result = _first_paragraph_with_see_also(text)
    assert "A checkbox input." in result
    assert "Follow these steps" not in result
    assert "See also: [Checkbox Group](https://example.com/)" in result


def test_first_paragraph_no_see_also():
    text = "A widget.\n\nFollow these steps.\n\n  1. Add it."
    result = _first_paragraph_with_see_also(text)
    assert result == "A widget.\n"


def test_generate_llms_full_txt_truncates_input_pages():
    sections = [Section(
        name="Components",
        pages=[],
        subsections=[Subsection(name="Inputs", pages=[
            Page(
                title="Slider",
                file_path="components/inputs/slider/index.qmd",
                content="---\ntitle: Slider\n---\n\nA slider widget.\n\nFollow these steps:\n\n  1. Add the slider.\n\nSee also: [Slider Range](https://shiny.posit.co/py/components/inputs/slider-range/)\n",
            ),
        ])],
    )]
    output = generate_llms_full_txt(sections)
    assert "A slider widget." in output
    assert "Follow these steps" not in output
    assert "See also: [Slider Range]" in output


def test_generate_llms_full_txt_keeps_full_output_pages():
    sections = [Section(
        name="Components",
        pages=[],
        subsections=[Subsection(name="Outputs", pages=[
            Page(
                title="Plot",
                file_path="components/outputs/plot-matplotlib/index.qmd",
                content="---\ntitle: Plot\n---\n\nA plot output.\n\nFollow three steps to display a plot.\n",
            ),
        ])],
    )]
    output = generate_llms_full_txt(sections)
    assert "A plot output." in output
    assert "Follow three steps to display a plot." in output


# ---------------------------------------------------------------------------
# _parse_frontmatter — direct unit tests
# ---------------------------------------------------------------------------

def test_parse_frontmatter_basic():
    data, body = _parse_frontmatter("---\ntitle: Hello\n---\nBody.")
    assert data == {"title": "Hello"}
    assert body == "Body."


def test_parse_frontmatter_no_frontmatter():
    content = "Just prose, no frontmatter."
    data, body = _parse_frontmatter(content)
    assert data == {}
    assert body == content


def test_parse_frontmatter_returns_body_only():
    data, body = _parse_frontmatter("---\ntitle: T\nformat: html\n---\n\nActual content.")
    assert "title" not in body
    assert "format" not in body
    assert "Actual content." in body


def test_parse_frontmatter_multiline_value():
    content = "---\ndescription: |\n  Line one.\n  Line two.\n---\nBody."
    data, body = _parse_frontmatter(content)
    assert "Line one." in data["description"]
    assert "Line two." in data["description"]
    assert body == "Body."


def test_parse_frontmatter_quoted_value_with_colon():
    data, _ = _parse_frontmatter('---\ntitle: "Hello: World"\n---\nBody.')
    assert data["title"] == "Hello: World"


def test_parse_frontmatter_invalid_yaml_returns_empty():
    # Invalid YAML should not raise — returns ({}, body) with frontmatter stripped
    data, body = _parse_frontmatter("---\nkey: [unclosed\n---\nBody.")
    assert data == {}
    assert body == "Body."


def test_parse_frontmatter_non_dict_yaml_returns_empty():
    # YAML scalar at top level (e.g., just a number) should coerce to {}
    data, body = _parse_frontmatter("---\n42\n---\nBody.")
    assert data == {}
    assert body == "Body."


def test_parse_frontmatter_missing_trailing_newline():
    # File that ends exactly at the closing --- with no trailing newline
    content = "---\ntitle: T\n---"
    data, body = _parse_frontmatter(content)
    assert data == {"title": "T"}
    assert body == ""
    # Frontmatter must NOT leak into body
    assert "title" not in body
    assert "---" not in body


def test_parse_frontmatter_pagetitle_preferred():
    data, _ = _parse_frontmatter('---\npagetitle: "Page Title"\ntitle: Regular\n---\nBody.')
    assert data["pagetitle"] == "Page Title"
    assert data["title"] == "Regular"


# ---------------------------------------------------------------------------
# clean_qmd_content — state machine edge cases
# ---------------------------------------------------------------------------

def test_cell_options_other_than_echo_include_are_dropped():
    # All #| lines should be stripped from visible code blocks, not just echo/include
    content = "```python\n#| label: fig-example\n#| fig-cap: A figure\nmy_code()\n```"
    result = clean_qmd_content(content)
    assert "#|" not in result
    assert "my_code()" in result


def test_unclosed_code_block_does_not_emit_content():
    # An unclosed code block should not emit buffered lines as prose.
    # Document current behavior: content is swallowed (not ideal, but at least not corrupt).
    content = "Before.\n\n```python\nswallowed_code()\n"
    result = clean_qmd_content(content)
    assert "Before." in result
    assert "swallowed_code" not in result


def test_combined_frontmatter_hidden_block_and_div():
    # Integration: multiple features active in one document
    content = (
        "---\ntitle: T\n---\n\n"
        "Intro.\n\n"
        ":::{.grid}\nGrid content.\n:::\n\n"
        "```python\n#| echo: false\nhidden_setup()\n```\n\n"
        "Outro."
    )
    result = clean_qmd_content(content)
    assert "title: T" not in result
    assert "Intro." in result
    assert "Grid content." in result
    assert ":::" not in result
    assert "hidden_setup" not in result
    assert "Outro." in result


def test_relevant_functions_heading_stripped():
    content = "## Relevant Functions\n\nSome content."
    result = clean_qmd_content(content)
    assert "## Relevant Functions" not in result
    assert "Some content." in result


def test_template_heading_at_level_three_stripped():
    content = "### Details\n\nContent under h3."
    result = clean_qmd_content(content)
    assert "### Details" not in result
    assert "Content under h3." in result


# ---------------------------------------------------------------------------
# _resolve_links — missing edge cases
# ---------------------------------------------------------------------------

def test_resolve_links_fragment_only_unchanged():
    # A fragment-only href should be returned unchanged
    content = "See [this section](#overview) for details."
    result = _resolve_links(content, "docs/page.qmd")
    assert "[this section](#overview)" in result


def test_resolve_links_mailto_unchanged():
    content = "Email [us](mailto:support@example.com)."
    result = _resolve_links(content, "docs/page.qmd")
    assert "mailto:support@example.com" in result


def test_resolve_links_fragment_on_relative_path_drops_fragment():
    # The fragment is intentionally dropped when resolving relative paths.
    content = "See [Foo](../checkbox/index.qmd#section)."
    result = _resolve_links(content, "components/inputs/button/index.qmd")
    assert "#section" not in result
    assert "https://shiny.posit.co/py/components/inputs/checkbox/" in result


# ---------------------------------------------------------------------------
# _strip_html_outside_code — missing edge cases
# ---------------------------------------------------------------------------

def test_strip_html_multiple_code_spans_on_one_line():
    line = "Use `<a>` for links and `<b>` for bold, but remove <span>this</span>."
    result = _strip_html_outside_code(line)
    assert "`<a>`" in result
    assert "`<b>`" in result
    assert "<span>" not in result
    assert "this" in result


def test_strip_html_line_already_blank_unaffected():
    # A line that was blank before HTML stripping should not be treated as "pure HTML"
    assert _strip_html_outside_code("") == ""
    assert _strip_html_outside_code("   ") == "   "
