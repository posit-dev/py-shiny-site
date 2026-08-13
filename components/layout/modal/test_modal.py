from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_modal_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    btn = controller.InputActionButton(page, "show")
    btn.click()

    modal_body = page.locator(".modal-body")
    expect(modal_body).to_be_visible()
    expect(modal_body).to_contain_text("This is a somewhat important message.")


def test_modal_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_modal_interaction(page, core_app)


def test_modal_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_modal_interaction(page, express_app)
