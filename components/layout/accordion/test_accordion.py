import re
from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_accordion_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    acc = controller.Accordion(page, "acc")
    acc.expect_panels(["Section A", "Section B", "Section C"])
    acc.expect_open(["Section A"])

    selected = controller.OutputCode(page, "selected")
    selected.expect_value(re.compile("Section A"))

    # Open only Section B; the others close.
    acc.set(["Section B"])
    acc.expect_open(["Section B"])
    selected.expect_value(re.compile("Section B"))


def test_accordion_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_accordion_interaction(page, core_app)


def test_accordion_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_accordion_interaction(page, express_app)
