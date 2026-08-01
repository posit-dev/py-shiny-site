from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_dark_mode_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    dark_mode_el = page.locator("input-dark-mode, .bslib-dark-mode-toggle, [id*='dark_mode'], button, input").first
    expect(dark_mode_el).to_be_visible()


def test_dark_mode_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_dark_mode_interaction(page, core_app)


def test_dark_mode_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_dark_mode_interaction(page, express_app)
