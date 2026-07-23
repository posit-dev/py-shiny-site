from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")


def test_core_app_smoke(page: Page, core_app: ShinyAppProc, smoke_test) -> None:
    smoke_test(page, core_app)
