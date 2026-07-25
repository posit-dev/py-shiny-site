from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
update_core_app = create_example_fixture(HERE / "app-variation-update-core.py")
update_express_app = create_example_fixture(HERE / "app-variation-update-express.py")


def _check_code_editor_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    editor = controller.InputCodeEditor(page, "code")
    editor.expect_language("python")

    value = controller.OutputCode(page, "value")
    value.expect_value("print('Hello, world!')")

    # Typed code reaches the server on Ctrl/Cmd+Enter.
    editor.set("print('Goodbye, world!')", submit=True)
    value.expect_value("print('Goodbye, world!')")


def test_code_editor_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_code_editor_interaction(page, core_app)


def test_code_editor_express_interaction(
    page: Page, express_app: ShinyAppProc
) -> None:
    _check_code_editor_interaction(page, express_app)


def _check_update_code_editor(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    editor = controller.InputCodeEditor(page, "code")
    editor.expect_language("python")
    editor.expect_value("def greet(name):\n    return f'Hello, {name}!'")
    editor.expect_read_only(False)

    # Selecting a language calls ui.update_code_editor() with a new
    # value + language.
    controller.InputSelect(page, "language").set("javascript")
    editor.expect_language("javascript")
    editor.expect_value("function greet(name) {\n  return `Hello, ${name}!`;\n}")

    # The switch toggles read_only via ui.update_code_editor().
    controller.InputSwitch(page, "read_only").set(True)
    editor.expect_read_only(True)


def test_update_code_editor_core(page: Page, update_core_app: ShinyAppProc) -> None:
    _check_update_code_editor(page, update_core_app)


def test_update_code_editor_express(
    page: Page, update_express_app: ShinyAppProc
) -> None:
    _check_update_code_editor(page, update_express_app)
