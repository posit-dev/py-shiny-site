import re
from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
preview_app = create_example_fixture(HERE / "app-detail-preview.py")


def _check_bookmark_button(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    letter = controller.InputRadioButtons(page, "letter")
    letter.expect_selected("A")
    letter.set("B")

    bookmark = controller.InputBookmarkButton(page)
    bookmark.expect_label("Bookmark...")
    bookmark.click()

    # The on_bookmarked callback updates the query string with the app state.
    expect(page).to_have_url(re.compile(r"letter"), timeout=10000)

    # Reloading the bookmarked URL restores the saved selection.
    page.goto(page.url)
    letter_restored = controller.InputRadioButtons(page, "letter")
    letter_restored.expect_selected("B")


def test_bookmark_button_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_bookmark_button(page, core_app)


def test_bookmark_button_express_interaction(
    page: Page, express_app: ShinyAppProc
) -> None:
    _check_bookmark_button(page, express_app)


def test_bookmark_button_preview_shows_modal(
    page: Page, preview_app: ShinyAppProc
) -> None:
    # The detail-preview app keeps Shiny's default behavior: clicking the
    # bookmark button shows a modal containing the bookmark URL.
    page.goto(preview_app.url)

    controller.InputBookmarkButton(page).click()
    expect(page.get_by_text("Bookmarked application link")).to_be_visible(
        timeout=10000
    )
