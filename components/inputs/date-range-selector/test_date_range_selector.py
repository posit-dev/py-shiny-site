from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_date_range_selector_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    daterange = controller.InputDateRange(page, "daterange")
    daterange.expect_label("Date range")

    out = page.locator("#value")
    expect(out).to_contain_text("2020-01-01 to")

    daterange.set(("2021-05-01", "2021-05-31"))
    daterange.expect_value(("2021-05-01", "2021-05-31"))
    expect(out).to_have_text("2021-05-01 to 2021-05-31")


def test_date_range_selector_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_date_range_selector_interaction(page, core_app)


def test_date_range_selector_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_date_range_selector_interaction(page, express_app)
