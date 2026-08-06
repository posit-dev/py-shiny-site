from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_checkbox_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    cb = controller.InputCheckbox(page, "checkbox")
    cb.expect_checked(False)

    out = page.locator("#value")
    expect(out).to_have_text("False")

    cb.set(True)
    cb.expect_checked(True)
    expect(out).to_have_text("True")

    cb.set(False)
    cb.expect_checked(False)
    expect(out).to_have_text("False")


def test_checkbox_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_checkbox_interaction(page, core_app)


def test_checkbox_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_checkbox_interaction(page, express_app)
