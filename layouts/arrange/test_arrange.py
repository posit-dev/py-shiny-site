from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

nest_core_app = create_example_fixture(HERE / "app-column-nest-core.py")
nest_express_app = create_example_fixture(HERE / "app-column-nest-express.py")
fillable_core_app = create_example_fixture(HERE / "app-fillable-core.py")
fillable_express_app = create_example_fixture(HERE / "app-fillable-express.py")
wrap_core_app = create_example_fixture(HERE / "app-layout-column-wrap-core.py")
wrap_express_app = create_example_fixture(HERE / "app-layout-column-wrap-express.py")
wrap_dynamic_core_app = create_example_fixture(
    HERE / "app-layout-column-wrap-dynamic-core.py"
)
wrap_dynamic_express_app = create_example_fixture(
    HERE / "app-layout-column-wrap-dynamic-express.py"
)
wrap_half_core_app = create_example_fixture(
    HERE / "app-layout-column-wrap-half-core.py"
)
wrap_half_express_app = create_example_fixture(
    HERE / "app-layout-column-wrap-half-express.py"
)
columns_core_app = create_example_fixture(HERE / "app-layout-columns-core.py")
columns_express_app = create_example_fixture(HERE / "app-layout-columns-express.py")
widths_core_app = create_example_fixture(HERE / "app-layout-columns-col-widths-core.py")
widths_express_app = create_example_fixture(
    HERE / "app-layout-columns-col-widths-express.py"
)
fixed_core_app = create_example_fixture(HERE / "app-page-fixed-core.py")
fixed_express_app = create_example_fixture(HERE / "app-page-fixed-express.py")
fluid_core_app = create_example_fixture(HERE / "app-page-fluid-core.py")
fluid_express_app = create_example_fixture(HERE / "app-page-fluid-express.py")
html_core_app = create_example_fixture(HERE / "app-page-html-core.py")
html_express_app = create_example_fixture(HERE / "app-page-html-express.py")


def _check_nest(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # "Card 2" wraps two nested cards, so no single element holds
    # exactly that text. Assert the card count plus the leaf texts.
    expect(page.locator(".card")).to_have_count(4)
    expect(page.get_by_text("Card 1", exact=True)).to_be_visible()
    expect(page.get_by_text("Card 2.1", exact=True)).to_be_visible()
    expect(page.get_by_text("Card 2.2", exact=True)).to_be_visible()


def test_arrange_nest_core(page: Page, nest_core_app: ShinyAppProc) -> None:
    _check_nest(page, nest_core_app)


def test_arrange_nest_express(page: Page, nest_express_app: ShinyAppProc) -> None:
    _check_nest(page, nest_express_app)


def _check_histogram(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    slider = controller.InputSlider(page, "n")
    slider.expect_value("20")

    plot = controller.OutputPlot(page, "histogram")
    expect(plot.loc).to_be_visible()

    slider.set("50")
    slider.expect_value("50")
    expect(plot.loc).to_be_visible()


def test_arrange_fillable_core(page: Page, fillable_core_app: ShinyAppProc) -> None:
    _check_histogram(page, fillable_core_app)


def test_arrange_fillable_express(
    page: Page, fillable_express_app: ShinyAppProc
) -> None:
    _check_histogram(page, fillable_express_app)


def test_arrange_fixed_core(page: Page, fixed_core_app: ShinyAppProc) -> None:
    _check_histogram(page, fixed_core_app)


def test_arrange_fixed_express(page: Page, fixed_express_app: ShinyAppProc) -> None:
    _check_histogram(page, fixed_express_app)


def test_arrange_fluid_core(page: Page, fluid_core_app: ShinyAppProc) -> None:
    _check_histogram(page, fluid_core_app)


def test_arrange_fluid_express(page: Page, fluid_express_app: ShinyAppProc) -> None:
    _check_histogram(page, fluid_express_app)


def _check_cards(page: Page, app: ShinyAppProc, names: list[str]) -> None:
    page.goto(app.url)

    cards = page.locator(".card")
    expect(cards).to_have_count(len(names))
    for name in names:
        expect(page.get_by_text(name, exact=True)).to_be_visible()


def test_arrange_wrap_core(page: Page, wrap_core_app: ShinyAppProc) -> None:
    _check_cards(page, wrap_core_app, ["Card 1", "Card 2", "Card 3"])


def test_arrange_wrap_express(page: Page, wrap_express_app: ShinyAppProc) -> None:
    _check_cards(page, wrap_express_app, ["Card 1", "Card 2", "Card 3"])


def test_arrange_wrap_dynamic_core(
    page: Page, wrap_dynamic_core_app: ShinyAppProc
) -> None:
    _check_cards(page, wrap_dynamic_core_app, ["Card 1", "Card 2", "Card 3", "Card 4"])


def test_arrange_wrap_dynamic_express(
    page: Page, wrap_dynamic_express_app: ShinyAppProc
) -> None:
    _check_cards(
        page, wrap_dynamic_express_app, ["Card 1", "Card 2", "Card 3", "Card 4"]
    )


def test_arrange_wrap_half_core(page: Page, wrap_half_core_app: ShinyAppProc) -> None:
    _check_cards(page, wrap_half_core_app, ["Card 1", "Card 2", "Card 3", "Card 4"])


def test_arrange_wrap_half_express(
    page: Page, wrap_half_express_app: ShinyAppProc
) -> None:
    _check_cards(page, wrap_half_express_app, ["Card 1", "Card 2", "Card 3", "Card 4"])


def test_arrange_columns_core(page: Page, columns_core_app: ShinyAppProc) -> None:
    _check_cards(page, columns_core_app, ["Card 1", "Card 2", "Card 3"])


def test_arrange_columns_express(page: Page, columns_express_app: ShinyAppProc) -> None:
    _check_cards(page, columns_express_app, ["Card 1", "Card 2", "Card 3"])


def test_arrange_widths_core(page: Page, widths_core_app: ShinyAppProc) -> None:
    _check_cards(page, widths_core_app, ["Card 1", "Card 2", "Card 3"])


def test_arrange_widths_express(page: Page, widths_express_app: ShinyAppProc) -> None:
    _check_cards(page, widths_express_app, ["Card 1", "Card 2", "Card 3"])


def _check_html(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    expect(page.get_by_text("A complete HTML document, served as-is")).to_be_visible()

    greeting = controller.OutputText(page, "greeting")
    greeting.expect_value("Hello, Shiny!")

    # The page is raw HTML: the input has no shiny-input-container
    # wrapper, so the InputText controller locator does not apply.
    page.locator("#name").fill("Python")
    greeting.expect_value("Hello, Python!")


def test_arrange_html_core(page: Page, html_core_app: ShinyAppProc) -> None:
    _check_html(page, html_core_app)


def test_arrange_html_express(page: Page, html_express_app: ShinyAppProc) -> None:
    _check_html(page, html_express_app)
