from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def test_progress_bar_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    page.goto(core_app.url)

    btn = controller.InputActionButton(page, "button")
    btn.click()

    out = page.locator("#compute")
    expect(out).to_have_text("Done computing!", timeout=10000)


def test_progress_bar_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    page.goto(express_app.url)

    btn = controller.InputActionButton(page, "do_compute")
    btn.click()

    out = page.locator("#compute")
    expect(out).to_have_text("Done computing!", timeout=10000)
