import re
from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
update_core_app = create_example_fixture(HERE / "app-variation-update-popover-core.py")
update_express_app = create_example_fixture(
    HERE / "app-variation-update-popover-express.py"
)


def _check_popover_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    popover = controller.Popover(page, "btn_popover")
    state = controller.OutputCode(page, "popover_state")

    popover.expect_active(False)
    state.expect_value(re.compile("False"))

    # Clicking the trigger opens the popover.
    popover.set(True)
    popover.expect_active(True)
    popover.expect_title("A popover")
    popover.expect_body("A message inside the popover.")
    state.expect_value(re.compile("True"))

    # Clicking the trigger again closes it.
    popover.set(False)
    popover.expect_active(False)
    state.expect_value(re.compile("False"))


def test_popover_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_popover_interaction(page, core_app)


def test_popover_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_popover_interaction(page, express_app)


def _check_update_popover_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    popover = controller.Popover(page, "btn_popover")
    show = controller.InputActionButton(page, "btn_show")
    close = controller.InputActionButton(page, "btn_close")

    popover.expect_active(False)

    # ui.update_popover(show=True) opens the popover from the server.
    show.click()
    popover.expect_active(True)
    popover.expect_body("A message inside the popover.")

    # ui.update_popover(show=False) closes it again.
    close.click()
    popover.expect_active(False)


def test_update_popover_core_interaction(
    page: Page, update_core_app: ShinyAppProc
) -> None:
    _check_update_popover_interaction(page, update_core_app)


def test_update_popover_express_interaction(
    page: Page, update_express_app: ShinyAppProc
) -> None:
    _check_update_popover_interaction(page, update_express_app)
