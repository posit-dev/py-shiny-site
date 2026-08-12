from pathlib import Path

from conftest import _num_file_sections, split_shinylive_app

SINGLE = "## file: app.py\nfrom shiny import App\n"
MULTI = (
    "## file: app.py\n"
    "from utils import greet\n"
    "print(greet())\n"
    "## file: utils.py\n"
    "def greet():\n"
    "    return 'hi'\n"
)


def test_num_file_sections_counts_markers():
    assert _num_file_sections(SINGLE) == 1
    assert _num_file_sections(MULTI) == 2
    assert _num_file_sections("from shiny import App\n") == 0


def test_split_shinylive_app_writes_each_section(tmp_path: Path):
    entry = split_shinylive_app(MULTI, tmp_path)
    assert entry == tmp_path / "app.py"
    assert (tmp_path / "app.py").read_text() == (
        "from utils import greet\nprint(greet())\n"
    )
    assert (tmp_path / "utils.py").read_text() == "def greet():\n    return 'hi'\n"
