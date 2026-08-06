from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_value_box_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    vbox = page.locator(".bslib-value-box, .value-box")
    expect(vbox).to_be_visible()
    expect(vbox).to_contain_text("KPI Title")
    expect(vbox).to_contain_text("$1 Billion Dollars")


def test_value_box_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_value_box_interaction(page, core_app)


def test_value_box_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_value_box_interaction(page, express_app)
