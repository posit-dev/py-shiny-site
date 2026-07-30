from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_great_tables_output(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # render_gt renders the GT table's HTML into the output_gt("sales_table")
    # container. There is no py-shiny controller for GT output, so assert on
    # the rendered table content directly.
    output = page.locator("#sales_table")
    table = output.locator("table.gt_table")
    expect(table).to_be_visible()

    # Header title/subtitle from .tab_header()
    expect(table).to_contain_text("Quarterly product performance")
    expect(table).to_contain_text("Revenue, profitability, and year-over-year growth")

    # Column spanner + relabeled columns from .tab_spanner()/.cols_label()
    expect(table).to_contain_text("Financials")
    expect(table).to_contain_text("YoY growth")

    # Row stub values and formatted cells (.fmt_currency()/.fmt_percent())
    expect(table).to_contain_text("Enterprise")
    expect(table).to_contain_text("$421,000")
    expect(table).to_contain_text("33.0%")

    # Source note from .tab_source_note()
    expect(table).to_contain_text("Source:")


def test_great_tables_core_output(page: Page, core_app: ShinyAppProc) -> None:
    _check_great_tables_output(page, core_app)


def test_great_tables_express_output(page: Page, express_app: ShinyAppProc) -> None:
    _check_great_tables_output(page, express_app)
