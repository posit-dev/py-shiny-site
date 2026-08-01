from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_output_ui_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    sw = controller.InputSwitch(page, "show_slider")
    sw.expect_checked(True)

    slider = controller.InputSlider(page, "slider")
    slider.expect_value("5")

    sw.set(False)
    sw.expect_checked(False)
    expect(page.locator("input#slider")).to_have_count(0)


def test_output_ui_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_output_ui_interaction(page, core_app)


def test_output_ui_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_output_ui_interaction(page, express_app)
