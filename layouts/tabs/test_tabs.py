from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

accordion_core_app = create_example_fixture(HERE / "app-accordion-core.py")
accordion_express_app = create_example_fixture(HERE / "app-accordion-express.py")
hidden_core_app = create_example_fixture(HERE / "app-tabset-hidden-core.py")
hidden_express_app = create_example_fixture(HERE / "app-tabset-hidden-express.py")
pill_card_core_app = create_example_fixture(HERE / "app-tabset-pill-card-core.py")
pill_card_express_app = create_example_fixture(HERE / "app-tabset-pill-card-express.py")
pill_list_core_app = create_example_fixture(HERE / "app-tabset-pill-list-core.py")
pill_list_express_app = create_example_fixture(HERE / "app-tabset-pill-list-express.py")
pills_core_app = create_example_fixture(HERE / "app-tabset-pills-core.py")
pills_express_app = create_example_fixture(HERE / "app-tabset-pills-express.py")
tab_card_core_app = create_example_fixture(HERE / "app-tabset-tab-card-core.py")
tab_card_express_app = create_example_fixture(HERE / "app-tabset-tab-card-express.py")
tab_core_app = create_example_fixture(HERE / "app-tabset-tab-core.py")
tab_express_app = create_example_fixture(HERE / "app-tabset-tab-express.py")
underline_card_core_app = create_example_fixture(
    HERE / "app-tabset-underline-card-core.py"
)
underline_card_express_app = create_example_fixture(
    HERE / "app-tabset-underline-card-express.py"
)
underline_core_app = create_example_fixture(HERE / "app-tabset-underline-core.py")
underline_express_app = create_example_fixture(HERE / "app-tabset-underline-express.py")


def _check_accordion(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    acc = controller.Accordion(page, "acc")
    acc.expect_panels(["Section A", "Section B", "Section C", "Section D", "Section E"])
    acc.expect_open(["Section A"])

    acc.set(["Section C"])
    acc.expect_open(["Section C"])


def test_tabs_accordion_core(page: Page, accordion_core_app: ShinyAppProc) -> None:
    _check_accordion(page, accordion_core_app)


def test_tabs_accordion_express(
    page: Page, accordion_express_app: ShinyAppProc
) -> None:
    _check_accordion(page, accordion_express_app)


def _check_hidden(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    tabs = controller.NavsetHidden(page, "hidden_tabs")
    tabs.expect_value("panel1")
    expect(tabs.nav_panel("panel1").loc_content).to_contain_text("Panel 1 content")

    controller.InputRadioButtons(page, "controller").set("2")
    tabs.expect_value("panel2")
    expect(tabs.nav_panel("panel2").loc_content).to_contain_text("Panel 2 content")

    controller.InputRadioButtons(page, "controller").set("3")
    tabs.expect_value("panel3")
    expect(tabs.nav_panel("panel3").loc_content).to_contain_text("Panel 3 content")


def test_tabs_hidden_core(page: Page, hidden_core_app: ShinyAppProc) -> None:
    _check_hidden(page, hidden_core_app)


def test_tabs_hidden_express(page: Page, hidden_express_app: ShinyAppProc) -> None:
    _check_hidden(page, hidden_express_app)


def _check_navset(nav, page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    navset = nav(page, "tab")
    # Each demo also ships an "Other links" menu with a fourth panel.
    # Title locators differ per navset type (menu text vs. panel D),
    # so assert the menu trigger directly.
    expect(page.get_by_text("Other links").first).to_be_visible()
    navset.expect_value("A")
    expect(page.get_by_text("Panel A content")).to_be_visible()

    navset.set("B")
    navset.expect_value("B")
    expect(page.get_by_text("Panel B content")).to_be_visible()

    navset.set("C")
    navset.expect_value("C")
    expect(page.get_by_text("Panel C content")).to_be_visible()


def test_tabs_pill_card_core(page: Page, pill_card_core_app: ShinyAppProc) -> None:
    _check_navset(controller.NavsetCardPill, page, pill_card_core_app)


def test_tabs_pill_card_express(
    page: Page, pill_card_express_app: ShinyAppProc
) -> None:
    _check_navset(controller.NavsetCardPill, page, pill_card_express_app)


def test_tabs_pill_list_core(page: Page, pill_list_core_app: ShinyAppProc) -> None:
    _check_navset(controller.NavsetPillList, page, pill_list_core_app)


def test_tabs_pill_list_express(
    page: Page, pill_list_express_app: ShinyAppProc
) -> None:
    _check_navset(controller.NavsetPillList, page, pill_list_express_app)


def test_tabs_pills_core(page: Page, pills_core_app: ShinyAppProc) -> None:
    _check_navset(controller.NavsetPill, page, pills_core_app)


def test_tabs_pills_express(page: Page, pills_express_app: ShinyAppProc) -> None:
    _check_navset(controller.NavsetPill, page, pills_express_app)


def test_tabs_tab_card_core(page: Page, tab_card_core_app: ShinyAppProc) -> None:
    _check_navset(controller.NavsetCardTab, page, tab_card_core_app)


def test_tabs_tab_card_express(page: Page, tab_card_express_app: ShinyAppProc) -> None:
    _check_navset(controller.NavsetCardTab, page, tab_card_express_app)


def test_tabs_tab_core(page: Page, tab_core_app: ShinyAppProc) -> None:
    _check_navset(controller.NavsetTab, page, tab_core_app)


def test_tabs_tab_express(page: Page, tab_express_app: ShinyAppProc) -> None:
    # The express app renders a pill navset, not a tab navset.
    _check_navset(controller.NavsetPill, page, tab_express_app)


def test_tabs_underline_card_core(
    page: Page, underline_card_core_app: ShinyAppProc
) -> None:
    _check_navset(controller.NavsetCardUnderline, page, underline_card_core_app)


def test_tabs_underline_card_express(
    page: Page, underline_card_express_app: ShinyAppProc
) -> None:
    _check_navset(controller.NavsetCardUnderline, page, underline_card_express_app)


def test_tabs_underline_core(page: Page, underline_core_app: ShinyAppProc) -> None:
    _check_navset(controller.NavsetUnderline, page, underline_core_app)


def test_tabs_underline_express(
    page: Page, underline_express_app: ShinyAppProc
) -> None:
    _check_navset(controller.NavsetUnderline, page, underline_express_app)
