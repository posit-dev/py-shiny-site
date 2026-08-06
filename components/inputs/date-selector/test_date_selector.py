from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_date_selector_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    date_input = controller.InputDate(page, "date")
    date_input.expect_label("Date")

    out = page.locator("#value")
    expect(out).to_be_visible()

    date_input.set("2026-07-27")
    date_input.expect_value("2026-07-27")
    expect(out).to_have_text("2026-07-27")


def test_date_selector_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_date_selector_interaction(page, core_app)


def test_date_selector_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_date_selector_interaction(page, express_app)
