import re
from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
styling_core_app = create_example_fixture(HERE / "app-variation-styling-core.py")
styling_express_app = create_example_fixture(HERE / "app-variation-styling-express.py")
reactive_core_app = create_example_fixture(HERE / "app-variation-reactive-core.py")
reactive_express_app = create_example_fixture(HERE / "app-variation-reactive-express.py")


def _table(page: Page):
    """The GT table rendered into the ``output_gt("sales_table")`` container.

    There is no py-shiny controller for GT output, so assert on the rendered
    table markup directly.
    """
    return page.locator("#sales_table").locator("table.gt_table")


def _check_great_tables_output(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    table = _table(page)
    expect(table).to_be_visible()

    # Header from .tab_header()
    expect(table).to_contain_text("Quarterly product performance")

    # Row stub values and formatted cells (.fmt_currency()/.fmt_percent())
    expect(table).to_contain_text("Enterprise")
    expect(table).to_contain_text("$421,000")
    expect(table).to_contain_text("33.0%")


def test_great_tables_core_output(page: Page, core_app: ShinyAppProc) -> None:
    _check_great_tables_output(page, core_app)


def test_great_tables_express_output(page: Page, express_app: ShinyAppProc) -> None:
    _check_great_tables_output(page, express_app)


def _check_styling(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    table = _table(page)
    expect(table).to_be_visible()

    # Subtitle from .tab_header(), stubhead label from .tab_stubhead()
    expect(table).to_contain_text("Revenue, profitability, and year-over-year growth")
    expect(table).to_contain_text("Product")

    # Column spanner + relabeled columns from .tab_spanner()/.cols_label()
    expect(table).to_contain_text("Financials")
    expect(table).to_contain_text("YoY growth")

    # Negative growth still formats via .fmt_percent(). Note GT emits a Unicode
    # minus sign (U+2212), not an ASCII hyphen.
    expect(table).to_contain_text("−3.0%")

    # .data_color() and .tab_style() write inline background-colors onto the
    # cells. Assert the styles actually landed, not just the text, since that is
    # what this variation demonstrates. (GT emits no `headers` attribute, so
    # target the cells by their formatted contents.)
    margin_cell = table.locator("td.gt_row", has_text=re.compile(r"^18\.0%$"))
    expect(margin_cell).to_have_attribute("style", re.compile("background-color"))

    # .tab_style() fills the Enterprise row with its own colour.
    enterprise_cell = table.locator("td.gt_row", has_text=re.compile(r"^\$421,000$"))
    expect(enterprise_cell).to_have_attribute(
        "style", re.compile("background-color: #e7f5ff")
    )

    source_note = table.locator(".gt_sourcenote")
    expect(source_note).to_contain_text("Source:")
    # .tab_source_note(md(...)) renders markdown, so the label is bold markup.
    expect(source_note.locator("strong")).to_have_text("Source:")


def test_great_tables_styling_core(page: Page, styling_core_app: ShinyAppProc) -> None:
    _check_styling(page, styling_core_app)


def test_great_tables_styling_express(
    page: Page, styling_express_app: ShinyAppProc
) -> None:
    _check_styling(page, styling_express_app)


def _check_reactive(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    table = _table(page)
    expect(table).to_be_visible()

    # The slider starts at 0, so every product is listed.
    for product in ("Essentials", "Plus", "Pro", "Teams", "Enterprise"):
        expect(table).to_contain_text(product)

    # Raising the threshold re-runs @render_gt and drops the cheaper products.
    # The slider's tick labels carry thousands separators.
    controller.InputSlider(page, "min_revenue").set("300,000")

    expect(table).to_contain_text("Pro")
    expect(table).to_contain_text("Enterprise")
    for product in ("Essentials", "Plus", "Teams"):
        expect(table).not_to_contain_text(product)


def test_great_tables_reactive_core(page: Page, reactive_core_app: ShinyAppProc) -> None:
    _check_reactive(page, reactive_core_app)


def test_great_tables_reactive_express(
    page: Page, reactive_express_app: ShinyAppProc
) -> None:
    _check_reactive(page, reactive_express_app)
