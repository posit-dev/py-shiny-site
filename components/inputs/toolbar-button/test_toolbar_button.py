from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_toolbar_button_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    btn_label = controller.InputActionButton(page, "label_only")
    btn_label.click()

    out = page.locator("#button_status")
    expect(out).to_contain_text("Label: 1")


def test_toolbar_button_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_toolbar_button_interaction(page, core_app)


def test_toolbar_button_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_toolbar_button_interaction(page, express_app)
