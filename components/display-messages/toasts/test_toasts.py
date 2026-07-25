import re
from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
show_hide_core_app = create_example_fixture(HERE / "app-variation-show-hide-core.py")
show_hide_express_app = create_example_fixture(
    HERE / "app-variation-show-hide-express.py"
)


def _check_toast_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    toast = controller.Toast(page, "message_toast")
    toast.expect_hidden()

    controller.InputActionButton(page, "show").click()
    toast.expect_visible()
    toast.expect_body("You have a new message!")
    toast.expect_header(re.compile("Inbox"))
    toast.expect_type("success")

    # Dismiss the toast with its close button.
    toast.loc.locator(".btn-close").click()
    toast.expect_hidden()


def _check_show_hide_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    toast = controller.Toast(page, "persistent_toast")
    toast.expect_hidden()

    controller.InputActionButton(page, "show").click()
    toast.expect_visible()
    toast.expect_body("This toast stays until you hide it.")

    # Hide the toast from the server via ui.hide_toast().
    controller.InputActionButton(page, "hide").click()
    toast.expect_hidden()


def test_toast_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_toast_interaction(page, core_app)


def test_toast_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_toast_interaction(page, express_app)


def test_toast_show_hide_core_interaction(
    page: Page, show_hide_core_app: ShinyAppProc
) -> None:
    _check_show_hide_interaction(page, show_hide_core_app)


def test_toast_show_hide_express_interaction(
    page: Page, show_hide_express_app: ShinyAppProc
) -> None:
    _check_show_hide_interaction(page, show_hide_express_app)
