from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_password_field_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    password = controller.InputPassword(page, "password")
    password.expect_value("mypassword1")

    out = page.locator("#value")
    expect(out).to_have_text("mypassword1")

    password.set("newsecret123")
    password.expect_value("newsecret123")
    expect(out).to_have_text("newsecret123")


def test_password_field_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_password_field_interaction(page, core_app)


def test_password_field_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_password_field_interaction(page, express_app)
