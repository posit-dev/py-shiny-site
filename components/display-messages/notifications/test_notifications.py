from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_notification_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    btn = controller.InputActionButton(page, "show")
    btn.click()

    notif = page.locator(".shiny-notification")
    expect(notif).to_be_visible()
    expect(notif).to_contain_text("This notification will disappear after 2 seconds.")


def test_notification_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_notification_interaction(page, core_app)


def test_notification_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_notification_interaction(page, express_app)
