from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_plot_seaborn_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    slider = controller.InputSlider(page, "n")
    slider.expect_value("20")

    plot = page.locator("#plot img, #plot svg, .shiny-plot-output img")
    expect(plot).to_be_visible()


def test_plot_seaborn_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_plot_seaborn_interaction(page, core_app)


def test_plot_seaborn_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_plot_seaborn_interaction(page, express_app)
