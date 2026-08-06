from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_select_single_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    select = controller.InputSelect(page, "select")
    select.expect_selected("1A")

    out = page.locator("#value")
    expect(out).to_have_text("1A")

    select.set("1B")
    select.expect_selected("1B")
    expect(out).to_have_text("1B")


def test_select_single_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_select_single_interaction(page, core_app)


def test_select_single_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_select_single_interaction(page, express_app)
