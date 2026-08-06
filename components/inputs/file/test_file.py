from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_file_interaction(page: Page, app: ShinyAppProc, tmp_path: Path) -> None:
    page.goto(app.url)

    file_input = controller.InputFile(page, "f")
    file_input.expect_label("Pick a file, any file")

    test_file = tmp_path / "sample.txt"
    test_file.write_text("hello file upload")

    file_input.set(str(test_file))
    file_input.expect_complete()

    out = page.locator("#txt")
    expect(out).to_contain_text("sample.txt")


def test_file_core_interaction(page: Page, core_app: ShinyAppProc, tmp_path: Path) -> None:
    _check_file_interaction(page, core_app, tmp_path)


def test_file_express_interaction(page: Page, express_app: ShinyAppProc, tmp_path: Path) -> None:
    _check_file_interaction(page, express_app, tmp_path)
