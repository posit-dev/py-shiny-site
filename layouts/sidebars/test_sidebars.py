from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

card_core_app = create_example_fixture(HERE / "app-sidebar-card-core.py")
card_express_app = create_example_fixture(HERE / "app-sidebar-card-express.py")
collapsed_core_app = create_example_fixture(HERE / "app-sidebar-collapsed-core.py")
collapsed_express_app = create_example_fixture(
    HERE / "app-sidebar-collapsed-express.py"
)
left_core_app = create_example_fixture(HERE / "app-sidebar-left-core.py")
left_express_app = create_example_fixture(HERE / "app-sidebar-left-express.py")
right_core_app = create_example_fixture(HERE / "app-sidebar-right-core.py")
right_express_app = create_example_fixture(HERE / "app-sidebar-right-express.py")


def _sidebar(page: Page):
    return page.locator("aside.sidebar")


def _check_sidebar_open(page: Page, app: ShinyAppProc, text: str = "Sidebar") -> None:
    page.goto(app.url)

    sidebar = _sidebar(page)
    expect(sidebar).to_be_visible()
    expect(sidebar).to_contain_text(text)


def test_sidebars_card_core(page: Page, card_core_app: ShinyAppProc) -> None:
    page.goto(card_core_app.url)

    _check_sidebar_open(page, card_core_app)
    expect(page.locator(".card-header")).to_contain_text("Card with sidebar")
    expect(page.get_by_text("Card content")).to_be_visible()


def test_sidebars_card_express(page: Page, card_express_app: ShinyAppProc) -> None:
    page.goto(card_express_app.url)

    expect(_sidebar(page)).to_be_visible()
    expect(page.locator(".card-header")).to_contain_text("Card with sidebar")
    expect(page.get_by_text("Card content")).to_be_visible()


def _check_collapsed(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    sidebar = _sidebar(page)
    # The sidebar starts closed, so its content is hidden.
    expect(sidebar).to_be_hidden()

    page.locator("button.collapse-toggle").first.click()
    expect(sidebar).to_be_visible()
    expect(sidebar).to_contain_text("Sidebar")

    page.locator("button.collapse-toggle").first.click()
    expect(sidebar).to_be_hidden()


def test_sidebars_collapsed_core(page: Page, collapsed_core_app: ShinyAppProc) -> None:
    _check_collapsed(page, collapsed_core_app)


def test_sidebars_collapsed_express(
    page: Page, collapsed_express_app: ShinyAppProc
) -> None:
    _check_collapsed(page, collapsed_express_app)


def test_sidebars_left_core(page: Page, left_core_app: ShinyAppProc) -> None:
    _check_sidebar_open(page, left_core_app)
    expect(page.get_by_text("Main content")).to_be_visible()


def test_sidebars_left_express(page: Page, left_express_app: ShinyAppProc) -> None:
    _check_sidebar_open(page, left_express_app)
    expect(page.get_by_text("Main content")).to_be_visible()


def test_sidebars_right_core(page: Page, right_core_app: ShinyAppProc) -> None:
    _check_sidebar_open(page, right_core_app)
    expect(page.get_by_text("Main content")).to_be_visible()


def test_sidebars_right_express(page: Page, right_express_app: ShinyAppProc) -> None:
    _check_sidebar_open(page, right_express_app)
    expect(page.get_by_text("Main content")).to_be_visible()
