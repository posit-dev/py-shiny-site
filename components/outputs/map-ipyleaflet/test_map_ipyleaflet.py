from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_map_ipyleaflet_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    m = page.locator("#map, .leaflet-container")
    expect(m).to_be_visible()


def test_map_ipyleaflet_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_map_ipyleaflet_interaction(page, core_app)


def test_map_ipyleaflet_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_map_ipyleaflet_interaction(page, express_app)
