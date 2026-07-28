from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_switch_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    sw = controller.InputSwitch(page, "switch")
    sw.expect_checked(False)

    out = page.locator("#value")
    expect(out).to_have_text("False")

    sw.set(True)
    sw.expect_checked(True)
    expect(out).to_have_text("True")

    sw.set(False)
    sw.expect_checked(False)
    expect(out).to_have_text("False")


def test_switch_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_switch_interaction(page, core_app)


def test_switch_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_switch_interaction(page, express_app)
