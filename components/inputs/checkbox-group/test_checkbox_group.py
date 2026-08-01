from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_checkbox_group_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    cbg = controller.InputCheckboxGroup(page, "checkbox_group")
    cbg.expect_selected([])

    out = page.locator("#value")
    expect(out).to_have_text("")

    cbg.set(["a", "c"])
    cbg.expect_selected(["a", "c"])
    expect(out).to_have_text("a, c")


def test_checkbox_group_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_checkbox_group_interaction(page, core_app)


def test_checkbox_group_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_checkbox_group_interaction(page, express_app)
