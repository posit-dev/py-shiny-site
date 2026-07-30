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
types_core_app = create_example_fixture(HERE / "app-variation-types-core.py")
types_express_app = create_example_fixture(HERE / "app-variation-types-express.py")
positions_core_app = create_example_fixture(HERE / "app-variation-positions-core.py")
positions_express_app = create_example_fixture(
    HERE / "app-variation-positions-express.py"
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

    # closable=False + auto-hide disabled means the user cannot dismiss it.
    assert toast.loc.locator(".btn-close").count() == 0

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


# Each variation's toasts carry an explicit `id=` so `controller.Toast` can target
# them; without one the toast id is auto-generated and untestable.
TYPES = [
    ("success", "toast_success", "Operation successful!"),
    ("info", "toast_info", "Here's some information."),
    ("warning", "toast_warning", "Warning: check your input."),
    ("danger", "toast_danger", "Error: operation failed."),
]

POSITIONS = [
    ("top_left", "toast_top_left", "top-left", "Top left position"),
    ("top_center", "toast_top_center", "top-center", "Top center position"),
    ("middle_center", "toast_middle_center", "middle-center", "Middle center position"),
    ("bottom_right", "toast_bottom_right", "bottom-right", "Bottom right position"),
]


def _check_types(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    for button_id, toast_id, body in TYPES:
        toast = controller.Toast(page, toast_id)
        toast.expect_hidden()

        controller.InputActionButton(page, button_id).click()
        toast.expect_visible()
        toast.expect_body(body)
        toast.expect_type(button_id)

        toast.loc.locator(".btn-close").click()
        toast.expect_hidden()


def _check_positions(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    for button_id, toast_id, position, body in POSITIONS:
        toast = controller.Toast(page, toast_id)
        toast.expect_hidden()

        controller.InputActionButton(page, button_id).click()
        toast.expect_visible()
        toast.expect_body(body)
        toast.expect_position(position)

        toast.loc.locator(".btn-close").click()
        toast.expect_hidden()


def test_toast_types_core(page: Page, types_core_app: ShinyAppProc) -> None:
    _check_types(page, types_core_app)


def test_toast_types_express(page: Page, types_express_app: ShinyAppProc) -> None:
    _check_types(page, types_express_app)


def test_toast_positions_core(page: Page, positions_core_app: ShinyAppProc) -> None:
    _check_positions(page, positions_core_app)


def test_toast_positions_express(
    page: Page, positions_express_app: ShinyAppProc
) -> None:
    _check_positions(page, positions_express_app)
