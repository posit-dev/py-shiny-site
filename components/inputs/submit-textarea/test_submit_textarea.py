from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
enter_key_core_app = create_example_fixture(HERE / "app-variation-enter-key-core.py")
enter_key_express_app = create_example_fixture(
    HERE / "app-variation-enter-key-express.py"
)
update_core_app = create_example_fixture(HERE / "app-variation-update-core.py")
update_express_app = create_example_fixture(HERE / "app-variation-update-express.py")


def _check_submit_textarea_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    textarea = controller.InputSubmitTextarea(page, "message")
    value = controller.OutputCode(page, "value")

    # No value reaches the server until the user submits.
    value.expect_value("Nothing submitted yet.")
    textarea.set("Just typing, not submitting")
    value.expect_value("Nothing submitted yet.")

    # Submitting sends the value. `set(submit=True)` clicks the submit button.
    textarea.set("Hello, Shiny!", submit=True)
    value.expect_value("You submitted: Hello, Shiny!")

    # The documented default shortcut is Ctrl+Enter (Cmd+Enter on Mac). Neither
    # `set(submit=True)` nor `submit()` presses it -- both just click the button --
    # so press the real combination here, or submit_key="enter+modifier" goes
    # untested.
    textarea.expect_data_needs_modifier(True)
    textarea.set("Sent with the keyboard")
    textarea.loc.press("ControlOrMeta+Enter")
    value.expect_value("You submitted: Sent with the keyboard")


def test_submit_textarea_core_interaction(
    page: Page, core_app: ShinyAppProc
) -> None:
    _check_submit_textarea_interaction(page, core_app)


def test_submit_textarea_express_interaction(
    page: Page, express_app: ShinyAppProc
) -> None:
    _check_submit_textarea_interaction(page, express_app)


def _check_enter_key_submits(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    textarea = controller.InputSubmitTextarea(page, "quick_message")
    value = controller.OutputCode(page, "value")

    # submit_key="enter" -> no Ctrl/Cmd modifier needed.
    textarea.expect_data_needs_modifier(False)
    value.expect_value("Nothing submitted yet.")

    textarea.set("Quick note")
    textarea.loc.press("Enter")
    value.expect_value("You submitted: Quick note")


def test_enter_key_core(page: Page, enter_key_core_app: ShinyAppProc) -> None:
    _check_enter_key_submits(page, enter_key_core_app)


def test_enter_key_express(page: Page, enter_key_express_app: ShinyAppProc) -> None:
    _check_enter_key_submits(page, enter_key_express_app)


def _check_update_submit_textarea(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    textarea = controller.InputSubmitTextarea(page, "comment")
    value = controller.OutputCode(page, "value")
    value.expect_value("Nothing submitted yet.")

    # The toolbar button fills in a template via ui.update_submit_textarea().
    template = "Thank you for your feedback. We appreciate your input!"
    controller.InputActionButton(page, "template").click()
    textarea.expect_value(template)

    # Submitting the updated value sends it to the server.
    textarea.submit()
    value.expect_value(f"You submitted: {template}")

    # The clear button empties the textarea via ui.update_submit_textarea().
    controller.InputActionButton(page, "clear").click()
    textarea.expect_value("")


def test_update_submit_textarea_core(
    page: Page, update_core_app: ShinyAppProc
) -> None:
    _check_update_submit_textarea(page, update_core_app)


def test_update_submit_textarea_express(
    page: Page, update_express_app: ShinyAppProc
) -> None:
    _check_update_submit_textarea(page, update_express_app)
