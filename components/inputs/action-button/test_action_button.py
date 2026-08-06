from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_action_button_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    btn = controller.InputActionButton(page, "action_button")
    btn.expect_label("Action")

    txt = controller.OutputText(page, "counter")
    btn.click()
    txt.expect_value("1")

    btn.click()
    txt.expect_value("2")


def test_action_button_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_action_button_interaction(page, core_app)


def test_action_button_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_action_button_interaction(page, express_app)
