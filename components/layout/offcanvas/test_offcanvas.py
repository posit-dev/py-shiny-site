import re
from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
placement_core_app = create_example_fixture(HERE / "app-variation-placement-core.py")
placement_express_app = create_example_fixture(
    HERE / "app-variation-placement-express.py"
)
server_control_core_app = create_example_fixture(
    HERE / "app-variation-server-control-core.py"
)
server_control_express_app = create_example_fixture(
    HERE / "app-variation-server-control-express.py"
)
show_core_app = create_example_fixture(HERE / "app-variation-show-core.py")
show_express_app = create_example_fixture(HERE / "app-variation-show-express.py")


def _check_offcanvas_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    panel = controller.Offcanvas(page, "panel")
    state = controller.OutputCode(page, "state")

    panel.expect_open(False)
    state.expect_value(re.compile("closed"))

    # The `trigger=` button opens the panel, and `input.panel()` tracks its state.
    controller.InputActionButton(page, "open").click()
    panel.expect_open(True)
    panel.expect_body(
        "An offcanvas panel slides in from the edge of the page.\n"
        "Close it with the button, the backdrop, or the Escape key."
    )
    state.expect_value(re.compile("open"))

    # The header's close button dismisses the panel.
    panel.close()
    panel.expect_open(False)
    state.expect_value(re.compile("closed"))


def test_offcanvas_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_offcanvas_interaction(page, core_app)


def test_offcanvas_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_offcanvas_interaction(page, express_app)


# (button id, offcanvas id, expected `offcanvas-*` placement class)
PLACEMENTS = [
    ("open_left", "left_panel", "offcanvas-start"),
    ("open_top", "top_panel", "offcanvas-top"),
    ("open_bottom", "bottom_panel", "offcanvas-bottom"),
]


def _check_placement(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    for button_id, panel_id, placement_class in PLACEMENTS:
        panel = controller.Offcanvas(page, panel_id)
        panel.expect_open(False)

        controller.InputActionButton(page, button_id).click()
        panel.expect_open(True)
        assert placement_class in (panel.loc.get_attribute("class") or "")

        panel.close()
        panel.expect_open(False)


def test_offcanvas_placement_core(page: Page, placement_core_app: ShinyAppProc) -> None:
    _check_placement(page, placement_core_app)


def test_offcanvas_placement_express(
    page: Page, placement_express_app: ShinyAppProc
) -> None:
    _check_placement(page, placement_express_app)


def _check_server_control(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    panel = controller.Offcanvas(page, "panel")
    state = controller.OutputCode(page, "state")

    panel.expect_open(False)
    state.expect_value(re.compile("closed"))

    # ui.toggle_offcanvas(show=True) opens a panel that has no trigger of its own.
    controller.InputActionButton(page, "show").click()
    panel.expect_open(True)
    state.expect_value(re.compile("open"))

    # ui.hide_offcanvas() closes it. The Hide button lives inside the panel: while
    # the panel is open its backdrop covers the buttons behind it, so a control
    # that closes the panel has to sit in the panel itself.
    hide = controller.InputActionButton(page, "hide")
    hide.click()
    panel.expect_open(False)
    state.expect_value(re.compile("closed"))

    # ui.toggle_offcanvas() opens the panel when it is closed.
    controller.InputActionButton(page, "toggle").click()
    panel.expect_open(True)
    state.expect_value(re.compile("open"))

    hide.click()
    panel.expect_open(False)
    state.expect_value(re.compile("closed"))


def test_offcanvas_server_control_core(
    page: Page, server_control_core_app: ShinyAppProc
) -> None:
    _check_server_control(page, server_control_core_app)


def test_offcanvas_server_control_express(
    page: Page, server_control_express_app: ShinyAppProc
) -> None:
    _check_server_control(page, server_control_express_app)


def _check_show_offcanvas(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    panel = controller.Offcanvas(page, "server_panel")

    # The panel does not exist in the UI at all until the server inserts it.
    assert panel.loc.count() == 0

    controller.InputActionButton(page, "show").click()
    panel.expect_open(True)
    panel.expect_body("This panel was created by the server, not the UI.")

    panel.close()
    panel.expect_open(False)


def test_offcanvas_show_core(page: Page, show_core_app: ShinyAppProc) -> None:
    _check_show_offcanvas(page, show_core_app)


def test_offcanvas_show_express(page: Page, show_express_app: ShinyAppProc) -> None:
    _check_show_offcanvas(page, show_express_app)
