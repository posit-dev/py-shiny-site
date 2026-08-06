from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_text_area_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    textarea = controller.InputTextArea(page, "textarea")
    textarea.expect_value("Hello World")

    out = page.locator("#value")
    expect(out).to_have_text("Hello World")

    textarea.set("Line 1\nLine 2")
    textarea.expect_value("Line 1\nLine 2")
    expect(out).to_have_text("Line 1\nLine 2")


def test_text_area_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_text_area_interaction(page, core_app)


def test_text_area_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_text_area_interaction(page, express_app)
