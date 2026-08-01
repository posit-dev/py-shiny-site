from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_selectize_single_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    selectize = controller.InputSelectize(page, "selectize")
    selectize.expect_selected(["1A"])

    out = page.locator("#value")
    expect(out).to_have_text("1A")


def test_selectize_single_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_selectize_single_interaction(page, core_app)


def test_selectize_single_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_selectize_single_interaction(page, express_app)
