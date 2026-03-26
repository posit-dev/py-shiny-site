import sys
from pathlib import Path

# Add scripts/ to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_llms_txt import clean_qmd_content


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
