from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_code_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    code = controller.OutputCode(page, "code")
    code.expect_value('print("Hello Shiny")')

    # Changing the input updates the rendered code.
    controller.InputText(page, "message").set("Goodbye Shiny")
    code.expect_value('print("Goodbye Shiny")')


def test_code_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_code_interaction(page, core_app)


def test_code_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_code_interaction(page, express_app)
