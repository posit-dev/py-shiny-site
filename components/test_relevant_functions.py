# components/test_relevant_functions.py
from pathlib import Path

import pytest

from _relevant_functions import (
    SKIP_TITLES,
    TitleResolutionError,
    extract_signature_block,
    flatten_python_block,
    normalize_title,
    resolve_title,
)

VALUE_BOX_QMD = """# ui.value_box { #shiny.ui.value_box }

```python
ui.value_box(
    title,
    value,
    *args,
    showcase=None,
    showcase_layout='left center',
    full_screen=False,
    theme=None,
    height=None,
    max_height=None,
    min_height=None,
    fill=True,
    class_=None,
    id=None,
    **kwargs,
)
```

Value box
"""

PROGRESS_QMD = """# ui.Progress { #shiny.ui.Progress }

```python
ui.Progress(min=0, max=1, session=None)
```

## Methods

### close { #shiny.ui.Progress.close }

```python
ui.Progress.close()
```

Close the progress bar.
"""


def _write_api(tmp_path: Path) -> Path:
    api = tmp_path / "core"
    api.mkdir()
    (api / "ui.value_box.qmd").write_text(VALUE_BOX_QMD)
    (api / "ui.Progress.qmd").write_text(PROGRESS_QMD)
    return api


def test_flatten_python_block_multiline():
    block = "ui.value_box(\n    title,\n    value,\n    **kwargs,\n)"
    assert flatten_python_block(block) == "ui.value_box(title, value, **kwargs)"


def test_flatten_python_block_no_args():
    assert flatten_python_block("ui.Progress.close()") == "ui.Progress.close()"


def test_normalize_title_strips_decorator_call_and_express():
    assert normalize_title("@render.plot") == "render.plot"
    assert normalize_title("ui.input_file()") == "ui.input_file"
    assert normalize_title("express.ui.input_file") == "ui.input_file"


def test_resolve_title_top_level_function(tmp_path):
    api = _write_api(tmp_path)
    href, sig = resolve_title("ui.value_box", api_dir=api)
    assert href == (
        "https://shiny.posit.co/py/api/core/ui.value_box.html#shiny.ui.value_box"
    )
    assert sig == (
        "ui.value_box(title, value, *args, showcase=None, "
        "showcase_layout='left center', full_screen=False, theme=None, "
        "height=None, max_height=None, min_height=None, fill=True, "
        "class_=None, id=None, **kwargs)"
    )


def test_resolve_title_method_uses_class_file_and_anchor(tmp_path):
    api = _write_api(tmp_path)
    href, sig = resolve_title("ui.Progress.close", api_dir=api)
    assert href == (
        "https://shiny.posit.co/py/api/core/ui.Progress.html"
        "#shiny.ui.Progress.close"
    )
    assert sig == "ui.Progress.close()"


def test_resolve_title_unresolvable_raises(tmp_path):
    api = _write_api(tmp_path)
    with pytest.raises(TitleResolutionError) as exc:
        resolve_title("ui.does_not_exist", api_dir=api)
    assert "ui.does_not_exist" in str(exc.value)


def test_extract_signature_block_missing_anchor_raises(tmp_path):
    with pytest.raises(TitleResolutionError):
        extract_signature_block(VALUE_BOX_QMD, "shiny.ui.nope")


def test_skip_titles_contains_external_and_instance_forms():
    assert "shinywidgets.output_widget" in SKIP_TITLES
    assert "chat.append_message()" in SKIP_TITLES


def test_find_index_qmds_discovers_many():
    from _relevant_functions import find_index_qmds

    qmds = find_index_qmds()
    assert len(qmds) > 40, f"expected >40 index.qmd files, found {len(qmds)}"
    assert all(q.endswith("index.qmd") for q in qmds)


def test_rewrite_is_idempotent(tmp_path, monkeypatch):
    """Rewriting an already-fresh page produces no further change."""
    from _relevant_functions import rewrite_relevant_functions

    api = _write_api(tmp_path)
    page = tmp_path / "comp" / "index.qmd"
    page.parent.mkdir(parents=True)
    page.write_text(
        "---\n"
        "title: X\n"
        "listing:\n"
        "- id: relevant-functions\n"
        "  template: t.ejs\n"
        "  template-params:\n"
        "    dir: comp/\n"
        "  contents:\n"
        "  - title: ui.value_box\n"
        "    href: stale\n"
        "    signature: stale\n"
        "---\n\n"
        "body\n"
    )
    monkeypatch.chdir(tmp_path)
    assert rewrite_relevant_functions("comp/index.qmd", api_dir=api) is True
    first = page.read_text()
    assert "core/ui.value_box.html#shiny.ui.value_box" in first
    assert "stale" not in first
    rewrite_relevant_functions("comp/index.qmd", api_dir=api)
    assert page.read_text() == first  # idempotent
