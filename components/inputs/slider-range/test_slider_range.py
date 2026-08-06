from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_slider_range_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    slider = controller.InputSlider(page, "slider")
    slider.expect_label("Slider")

    out = page.locator("#value")
    expect(out).to_have_text("(35, 65)")


def test_slider_range_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_slider_range_interaction(page, core_app)


def test_slider_range_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_slider_range_interaction(page, express_app)
