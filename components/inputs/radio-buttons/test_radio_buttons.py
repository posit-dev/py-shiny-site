from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_radio_buttons_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    radio = controller.InputRadioButtons(page, "radio")
    radio.expect_selected("1")

    out = page.locator("#value")
    expect(out).to_have_text("1")

    radio.set("2")
    radio.expect_selected("2")
    expect(out).to_have_text("2")


def test_radio_buttons_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_radio_buttons_interaction(page, core_app)


def test_radio_buttons_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_radio_buttons_interaction(page, express_app)
