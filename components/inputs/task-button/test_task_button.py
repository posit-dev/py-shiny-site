import re
from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
variation_core_app = create_example_fixture(HERE / "app-variation-update-core.py")
variation_express_app = create_example_fixture(HERE / "app-variation-update-express.py")
extended_core_app = create_example_fixture(HERE / "app-variation-extended-task-core.py")
extended_express_app = create_example_fixture(
    HERE / "app-variation-extended-task-express.py"
)
kitchensink_core_app = create_example_fixture(HERE / "app-kitchensink-core.py")
kitchensink_express_app = create_example_fixture(HERE / "app-kitchensink-express.py")


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


def _check_extended_task(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    compute = controller.InputTaskButton(page, "compute")
    clock = controller.OutputCode(page, "current_time")
    result = controller.OutputCode(page, "result")

    compute.expect_state("ready")
    expect(clock.loc).not_to_have_text("")

    before = clock.loc.inner_text()
    compute.click()
    compute.expect_state("busy")

    # The point of extended_task: the reactive graph is NOT blocked, so the
    # invalidate_later-driven clock keeps updating *while* the task is running.
    # A plain `time.sleep()`/`await asyncio.sleep()` in a render function would
    # freeze this output until the task finished.
    expect(clock.loc).not_to_have_text(before, timeout=5000)
    compute.expect_state("busy")

    # x=1, y=2 -> 3, once the 3s task resolves.
    result.expect_value("3", timeout=15000)
    compute.expect_state("ready")


def _check_extended_task_cancel(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    compute = controller.InputTaskButton(page, "compute")
    compute.click()
    compute.expect_state("busy")

    # `.cancel()` interrupts the task, which releases the bound button.
    controller.InputActionButton(page, "cancel").click()
    compute.expect_state("ready", timeout=10000)


def test_task_button_extended_task_core(
    page: Page, extended_core_app: ShinyAppProc
) -> None:
    _check_extended_task(page, extended_core_app)


def test_task_button_extended_task_express(
    page: Page, extended_express_app: ShinyAppProc
) -> None:
    _check_extended_task(page, extended_express_app)


def test_task_button_extended_task_cancel(
    page: Page, extended_core_app: ShinyAppProc
) -> None:
    _check_extended_task_cancel(page, extended_core_app)


def _check_kitchensink(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    btn = controller.InputTaskButton(page, "task_button")
    btn.expect_label_ready("Run task")
    btn.expect_label_busy("Crunching numbers...")
    btn.expect_width("300px")
    btn.expect_auto_reset(False)
    # type="warning" renders as the Bootstrap contextual class.
    expect(btn.loc).to_have_class(re.compile(r"btn-warning"))
    # Both icon= and icon_busy= are rendered (ready + busy slots).
    assert btn.loc.locator("svg").count() >= 1


def test_task_button_kitchensink_core(
    page: Page, kitchensink_core_app: ShinyAppProc
) -> None:
    _check_kitchensink(page, kitchensink_core_app)


def test_task_button_kitchensink_express(
    page: Page, kitchensink_express_app: ShinyAppProc
) -> None:
    _check_kitchensink(page, kitchensink_express_app)
