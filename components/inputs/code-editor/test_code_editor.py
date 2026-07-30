from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
languages_core_app = create_example_fixture(HERE / "app-variation-languages-core.py")
languages_express_app = create_example_fixture(
    HERE / "app-variation-languages-express.py"
)
update_core_app = create_example_fixture(HERE / "app-variation-update-core.py")
update_express_app = create_example_fixture(HERE / "app-variation-update-express.py")
kitchensink_core_app = create_example_fixture(HERE / "app-kitchensink-core.py")
kitchensink_express_app = create_example_fixture(HERE / "app-kitchensink-express.py")


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


def _check_languages(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Each editor keeps the `language` it was created with, which is what drives
    # syntax highlighting. These apps have no server logic, so the language
    # attribute is the only observable effect the variation promises.
    for editor_id, language, value in (
        ("python_code", "python", "def hello():\n    print('Hello, Python!')"),
        (
            "javascript_code",
            "javascript",
            "function hello() {\n  console.log('Hello, JavaScript!');\n}",
        ),
        ("sql_code", "sql", "SELECT * FROM users\nWHERE active = true;"),
    ):
        editor = controller.InputCodeEditor(page, editor_id)
        editor.expect_language(language)
        editor.expect_value(value)


def test_languages_core(page: Page, languages_core_app: ShinyAppProc) -> None:
    _check_languages(page, languages_core_app)


def test_languages_express(page: Page, languages_express_app: ShinyAppProc) -> None:
    _check_languages(page, languages_express_app)


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


def _check_kitchensink(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    editor = controller.InputCodeEditor(page, "editor")

    # The kitchen sink exists to exercise every parameter, so assert the ones
    # that are otherwise undemonstrated anywhere on the page.
    editor.expect_language("python")
    editor.expect_height("260px")
    editor.expect_width("100%")
    editor.expect_theme_light("github-light")
    editor.expect_theme_dark("github-dark")
    editor.expect_read_only(False)
    editor.expect_line_numbers(True)
    editor.expect_word_wrap(True)
    editor.expect_tab_size(4)

    # It is still a working editor: Ctrl/Cmd+Enter sends the value.
    value = controller.OutputCode(page, "submitted")
    editor.set("print('kitchen sink')", submit=True)
    value.expect_value("print('kitchen sink')")


def test_kitchensink_core(page: Page, kitchensink_core_app: ShinyAppProc) -> None:
    _check_kitchensink(page, kitchensink_core_app)


def test_kitchensink_express(page: Page, kitchensink_express_app: ShinyAppProc) -> None:
    _check_kitchensink(page, kitchensink_express_app)
