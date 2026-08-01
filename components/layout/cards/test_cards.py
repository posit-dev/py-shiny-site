from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_card_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    card = page.locator(".card")
    expect(card).to_be_visible()

    card_header = page.locator(".card-header")
    expect(card_header).to_contain_text("Sales Trend")

    plot = page.locator(".shiny-plot-output")
    expect(plot).to_be_visible()


def test_card_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_card_interaction(page, core_app)


def test_card_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_card_interaction(page, express_app)
