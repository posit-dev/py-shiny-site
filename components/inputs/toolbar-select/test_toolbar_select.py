from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_toolbar_select_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    select = controller.InputSelect(page, "view_mode")
    select.expect_selected("Table")

    out = page.locator("#selected_view")
    expect(out).to_contain_text("View Mode: Table")

    select.set("Chart")
    expect(out).to_contain_text("View Mode: Chart")


def test_toolbar_select_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_toolbar_select_interaction(page, core_app)


def test_toolbar_select_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_toolbar_select_interaction(page, express_app)
