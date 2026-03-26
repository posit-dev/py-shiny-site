import sys
from pathlib import Path

# Add scripts/ to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_llms_txt import (
    SidebarEntry,
    clean_qmd_content,
    clean_section_name,
    extract_title,
    file_path_to_url,
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


def test_walk_skips_anchor_links():
    entries = list(walk_sidebar([{"text": "X", "href": "/page.html#section"}]))
    assert entries == []


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
