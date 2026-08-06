from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_chat_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    chat_container = page.locator("#chat")
    expect(chat_container).to_be_visible()

    # The input element inside shiny-chat / shadow root
    chat_input = page.locator("#chat").locator("textarea, input").first
    if chat_input.count() > 0:
        chat_input.fill("Hello bot")
        chat_input.press("Enter")
        expect(chat_container).to_contain_text("You said: Hello bot")


def test_chat_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_chat_interaction(page, core_app)


def test_chat_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_chat_interaction(page, express_app)
