import re
from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

navbar_top_app = create_example_fixture(HERE / "app-navbar-top.py")
navbar_top_express_app = create_example_fixture(HERE / "app-navbar-top-express.py")
navbar_bottom_app = create_example_fixture(HERE / "app-navbar-bottom.py")
navbar_bottom_express_app = create_example_fixture(
    HERE / "app-navbar-bottom-express.py"
)
navset_bar_core_app = create_example_fixture(HERE / "app-navset-bar-core.py")
navset_bar_express_app = create_example_fixture(HERE / "app-navset-bar-express.py")


def _check_page_navbar(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    navbar = controller.PageNavbar(page, "page")
    navbar.expect_title("App with navbar")
    navbar.expect_nav_titles(["A", "B", "C"])
    navbar.expect_value("A")
    expect(page.get_by_text("Page A content")).to_be_visible()

    navbar.set("B")
    navbar.expect_value("B")
    expect(page.get_by_text("Page B content")).to_be_visible()

    navbar.set("C")
    navbar.expect_value("C")
    expect(page.get_by_text("Page C content")).to_be_visible()


def test_navbars_top(page: Page, navbar_top_app: ShinyAppProc) -> None:
    _check_page_navbar(page, navbar_top_app)


def test_navbars_top_express(page: Page, navbar_top_express_app: ShinyAppProc) -> None:
    _check_page_navbar(page, navbar_top_express_app)


def test_navbars_bottom(page: Page, navbar_bottom_app: ShinyAppProc) -> None:
    _check_page_navbar(page, navbar_bottom_app)


def test_navbars_bottom_express(
    page: Page, navbar_bottom_express_app: ShinyAppProc
) -> None:
    _check_page_navbar(page, navbar_bottom_express_app)


def _check_navset_bar(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    bar = controller.NavsetBar(page, "section")
    bar.expect_title("Sections")
    bar.expect_value("Summary")
    expect(page.get_by_text("Summary content")).to_be_visible()

    selected = controller.OutputCode(page, "selected")
    selected.expect_value(re.compile("Summary"))

    bar.set("Details")
    bar.expect_value("Details")
    expect(page.get_by_text("Details content")).to_be_visible()
    selected.expect_value(re.compile("Details"))

    bar.set("About")
    bar.expect_value("About")
    expect(page.get_by_text("About content")).to_be_visible()
    selected.expect_value(re.compile("About"))


def test_navbars_navset_bar_core(page: Page, navset_bar_core_app: ShinyAppProc) -> None:
    _check_navset_bar(page, navset_bar_core_app)


def test_navbars_navset_bar_express(
    page: Page, navset_bar_express_app: ShinyAppProc
) -> None:
    _check_navset_bar(page, navset_bar_express_app)
