from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_toolbar_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    btn = controller.InputActionButton(page, "action1")
    btn.click()

    out = page.locator("#toolbar_status")
    expect(out).to_contain_text("Button clicks: 1")


def test_toolbar_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_toolbar_interaction(page, core_app)


def test_toolbar_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_toolbar_interaction(page, express_app)
