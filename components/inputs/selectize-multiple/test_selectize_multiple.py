from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_selectize_multiple_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    selectize = controller.InputSelectize(page, "selectize")
    selectize.expect_multiple(True)

    out = page.locator("#value")
    expect(out).to_have_text("()")


def test_selectize_multiple_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_selectize_multiple_interaction(page, core_app)


def test_selectize_multiple_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_selectize_multiple_interaction(page, express_app)
