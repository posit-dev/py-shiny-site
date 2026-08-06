from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_text_box_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    text_input = controller.InputText(page, "text")
    text_input.expect_value("Enter text...")

    out = page.locator("#value")
    expect(out).to_have_text("Enter text...")

    text_input.set("Hello Shiny!")
    text_input.expect_value("Hello Shiny!")
    expect(out).to_have_text("Hello Shiny!")


def test_text_box_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_text_box_interaction(page, core_app)


def test_text_box_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_text_box_interaction(page, express_app)
