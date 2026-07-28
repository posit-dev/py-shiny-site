from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_tooltip_interaction(page: Page, app: ShinyAppProc, expected_body: str) -> None:
    page.goto(app.url)

    tooltip = controller.Tooltip(page, "btn_tooltip")

    # Open tooltip
    tooltip.set(True)
    tooltip.expect_body(expected_body)

    # Close tooltip by hovering away
    page.mouse.move(0, 0)



def test_tooltip_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_tooltip_interaction(page, core_app, "A message")


def test_tooltip_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_tooltip_interaction(page, express_app, "The tooltip message")
