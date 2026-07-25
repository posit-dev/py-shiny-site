from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
variation_core_app = create_example_fixture(HERE / "app-variation-update-core.py")
variation_express_app = create_example_fixture(HERE / "app-variation-update-express.py")


def _check_task_button(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    btn = controller.InputTaskButton(page, "task_button")
    btn.expect_state("ready")
    btn.expect_label_ready("Run task")
    btn.expect_label_busy("Processing...")

    btn.click()
    # The button flips to busy immediately, while the task runs on the server.
    btn.expect_state("busy")

    # Once the task finishes, the result appears and the button auto-resets.
    result = controller.OutputCode(page, "result")
    result.expect_value("Task completed 1 time(s)", timeout=10000)
    btn.expect_state("ready")


def _check_manual_reset(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    run = controller.InputTaskButton(page, "run")
    run.expect_state("ready")
    run.expect_auto_reset(False)

    run.click()
    run.expect_state("busy")

    # The task completes, but with auto_reset=False the button stays busy...
    result = controller.OutputCode(page, "result")
    result.expect_value("Task completed 1 time(s)", timeout=10000)
    run.expect_state("busy")

    # ...until ui.update_task_button(state="ready") is triggered.
    controller.InputActionButton(page, "reset").click()
    run.expect_state("ready")


def test_task_button_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_task_button(page, core_app)


def test_task_button_express_interaction(
    page: Page, express_app: ShinyAppProc
) -> None:
    _check_task_button(page, express_app)


def test_task_button_manual_reset_core(
    page: Page, variation_core_app: ShinyAppProc
) -> None:
    _check_manual_reset(page, variation_core_app)


def test_task_button_manual_reset_express(
    page: Page, variation_express_app: ShinyAppProc
) -> None:
    _check_manual_reset(page, variation_express_app)
