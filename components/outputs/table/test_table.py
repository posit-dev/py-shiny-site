from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_table_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    table = controller.OutputTable(page, "table")
    table.expect_column_labels(["Model", "MPG", "Cylinders", "Horsepower"])
    table.expect_column_text(1, ["Mazda RX4", "Datsun 710", "Merc 240D"])

    # Moving the slider changes how many rows are rendered.
    controller.InputSlider(page, "rows").set("5")
    table.expect_column_text(
        1,
        ["Mazda RX4", "Datsun 710", "Merc 240D", "Fiat 128", "Volvo 142E"],
    )


def test_table_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_table_interaction(page, core_app)


def test_table_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_table_interaction(page, express_app)
