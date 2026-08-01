from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_numeric_input_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    num = controller.InputNumeric(page, "numeric")
    num.expect_value("1")

    out = page.locator("#value")
    expect(out).to_have_text("1")

    num.set("5")
    num.expect_value("5")
    expect(out).to_have_text("5")


def test_numeric_input_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_numeric_input_interaction(page, core_app)


def test_numeric_input_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_numeric_input_interaction(page, express_app)
