from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

card_sidebar_core_app = create_example_fixture(HERE / "app-card-sidebar-core.py")
card_sidebar_express_app = create_example_fixture(HERE / "app-card-sidebar-express.py")
filling_core_app = create_example_fixture(HERE / "app-filling-outputs-core.py")
filling_express_app = create_example_fixture(HERE / "app-filling-outputs-express.py")
hello_core_app = create_example_fixture(HERE / "app-hello-card-core.py")
hello_express_app = create_example_fixture(HERE / "app-hello-card-express.py")
implicit_core_app = create_example_fixture(HERE / "app-implicit-card-body-core.py")
implicit_express_app = create_example_fixture(
    HERE / "app-implicit-card-body-express.py"
)
multiple_core_app = create_example_fixture(HERE / "app-multiple-cards-core.py")
multiple_express_app = create_example_fixture(HERE / "app-multiple-cards-express.py")
absolute_core_app = create_example_fixture(HERE / "app-panel-absolute-core.py")
absolute_express_app = create_example_fixture(HERE / "app-panel-absolute-express.py")
conditional_core_app = create_example_fixture(HERE / "app-panel-conditional-core.py")
conditional_express_app = create_example_fixture(
    HERE / "app-panel-conditional-express.py"
)
restricting_core_app = create_example_fixture(HERE / "app-restricting-growth-core.py")
restricting_express_app = create_example_fixture(
    HERE / "app-restricting-growth-express.py"
)
tabbed_core_app = create_example_fixture(HERE / "app-tabbed-card-core.py")
tabbed_express_app = create_example_fixture(HERE / "app-tabbed-card-express.py")
two_core_app = create_example_fixture(HERE / "app-two-cards-core.py")
two_express_app = create_example_fixture(HERE / "app-two-cards-express.py")


def _check_card_sidebar(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    expect(page.locator(".card-header")).to_contain_text("Flower Data Explorer")

    table = controller.OutputDataFrame(page, "flower_table")
    table.expect_nrow(5)

    # Filter to red flowers (Rose, Poppy).
    controller.InputSelect(page, "color_filter").set("Red")
    table.expect_nrow(2)

    # Limit the row count.
    controller.InputSelect(page, "color_filter").set("All")
    controller.InputSlider(page, "rows").set("2")
    table.expect_nrow(2)

    # Reset restores the defaults.
    controller.InputActionButton(page, "reset").click()
    controller.InputSelect(page, "color_filter").expect_selected("All")
    table.expect_nrow(5)


def test_panels_cards_card_sidebar_core(
    page: Page, card_sidebar_core_app: ShinyAppProc
) -> None:
    _check_card_sidebar(page, card_sidebar_core_app)


def test_panels_cards_card_sidebar_express(
    page: Page, card_sidebar_express_app: ShinyAppProc
) -> None:
    _check_card_sidebar(page, card_sidebar_express_app)


def _check_filling(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    expect(page.locator(".card-header")).to_contain_text("A filling plot")
    plot = controller.OutputPlot(page, "plot")
    expect(plot.loc).to_be_visible()


def test_panels_cards_filling_core(page: Page, filling_core_app: ShinyAppProc) -> None:
    _check_filling(page, filling_core_app)


def test_panels_cards_filling_express(
    page: Page, filling_express_app: ShinyAppProc
) -> None:
    _check_filling(page, filling_express_app)


def _check_hello_card(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    expect(page.locator(".card-header")).to_contain_text("A header")
    expect(page.locator(".card-body")).to_contain_text("Some text")
    expect(page.locator(".card-body a")).to_have_attribute("href", "https://github.com")


def test_panels_cards_hello_core(page: Page, hello_core_app: ShinyAppProc) -> None:
    _check_hello_card(page, hello_core_app)


def test_panels_cards_hello_express(
    page: Page, hello_express_app: ShinyAppProc
) -> None:
    _check_hello_card(page, hello_express_app)


def test_panels_cards_implicit_core(
    page: Page, implicit_core_app: ShinyAppProc
) -> None:
    _check_hello_card(page, implicit_core_app)


def test_panels_cards_implicit_express(
    page: Page, implicit_express_app: ShinyAppProc
) -> None:
    _check_hello_card(page, implicit_express_app)


def _check_multiple(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    cards = page.locator(".card")
    expect(cards).to_have_count(2)
    expect(page.get_by_text("Content for card 1")).to_be_visible()
    expect(page.get_by_text("Content for card 2")).to_be_visible()


def test_panels_cards_multiple_core(
    page: Page, multiple_core_app: ShinyAppProc
) -> None:
    _check_multiple(page, multiple_core_app)


def test_panels_cards_multiple_express(
    page: Page, multiple_express_app: ShinyAppProc
) -> None:
    _check_multiple(page, multiple_express_app)


def _check_absolute(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # panel_absolute renders a plain positioned div (class "draggable"
    # when draggable). Assert the wrapped card shows inside it.
    panel = page.locator("div.draggable")
    expect(panel).to_be_visible()
    expect(panel).to_contain_text("Draggable panel")
    expect(panel).to_contain_text("Move this panel anywhere you want.")


def test_panels_cards_absolute_core(
    page: Page, absolute_core_app: ShinyAppProc
) -> None:
    _check_absolute(page, absolute_core_app)


def test_panels_cards_absolute_express(
    page: Page, absolute_express_app: ShinyAppProc
) -> None:
    _check_absolute(page, absolute_express_app)


def _check_conditional(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    kind = page.locator("#kind")
    slider = page.locator("#slider")
    select = page.locator("#select")

    # Advanced options start hidden.
    expect(kind).to_be_hidden()
    expect(slider).to_be_hidden()
    expect(select).to_be_hidden()

    controller.InputCheckbox(page, "show").set(True)
    expect(kind).to_be_visible()

    # The slider shows by default; the select stays hidden.
    expect(slider).to_be_visible()
    expect(select).to_be_hidden()

    controller.InputRadioButtons(page, "kind").set("select")
    expect(slider).to_be_hidden()
    expect(select).to_be_visible()

    controller.InputCheckbox(page, "show").set(False)
    expect(kind).to_be_hidden()


def test_panels_cards_conditional_core(
    page: Page, conditional_core_app: ShinyAppProc
) -> None:
    _check_conditional(page, conditional_core_app)


def test_panels_cards_conditional_express(
    page: Page, conditional_express_app: ShinyAppProc
) -> None:
    _check_conditional(page, conditional_express_app)


def _check_restricting(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    expect(page.locator(".card-header")).to_contain_text(
        "A long, scrolling, description"
    )
    expect(page.locator(".card-body")).to_contain_text("Lorem ipsum")


def test_panels_cards_restricting_core(
    page: Page, restricting_core_app: ShinyAppProc
) -> None:
    _check_restricting(page, restricting_core_app)


def test_panels_cards_restricting_express(
    page: Page, restricting_express_app: ShinyAppProc
) -> None:
    _check_restricting(page, restricting_express_app)


def _check_tabbed(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    expect(page.get_by_text("Project Dashboard")).to_be_visible()
    expect(page.get_by_text("3 milestones and 12 tasks")).to_be_visible()

    page.get_by_role("tab", name="Team").click()
    expect(page.get_by_text("Alice (Lead)")).to_be_visible()

    page.get_by_role("tab", name="Timeline").click()
    expect(page.get_by_text("Start: January 2026")).to_be_visible()


def test_panels_cards_tabbed_core(page: Page, tabbed_core_app: ShinyAppProc) -> None:
    _check_tabbed(page, tabbed_core_app)


def test_panels_cards_tabbed_express(
    page: Page, tabbed_express_app: ShinyAppProc
) -> None:
    _check_tabbed(page, tabbed_express_app)


def _check_two_cards(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    expect(page.locator(".card-header").first).to_contain_text("User Settings")
    expect(page.locator(".card-header").nth(1)).to_contain_text("Activity Summary")

    summary = controller.OutputText(page, "summary")
    summary.expect_value("Hello, John Doe!")

    controller.InputText(page, "name").set("Ada")
    summary.expect_value("Hello, Ada!")

    controller.InputActionButton(page, "save").click()
    summary.expect_value("Hello, Ada!")


def test_panels_cards_two_core(page: Page, two_core_app: ShinyAppProc) -> None:
    _check_two_cards(page, two_core_app)


def test_panels_cards_two_express(page: Page, two_express_app: ShinyAppProc) -> None:
    _check_two_cards(page, two_express_app)
