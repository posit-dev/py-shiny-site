from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_action_link_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    link = page.locator("#action_link")
    expect(link).to_be_visible()
    expect(link).to_contain_text("Increase Number")

    out = page.locator("#counter")
    expect(out).to_have_text("0")

    link.click()
    expect(out).to_have_text("1")

    link.click()
    expect(out).to_have_text("2")


def test_action_link_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_action_link_interaction(page, core_app)


def test_action_link_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_action_link_interaction(page, express_app)
