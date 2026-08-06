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
multiple_core_app = create_example_fixture(HERE / "app-variation-multiple-core.py")
multiple_express_app = create_example_fixture(
    HERE / "app-variation-multiple-express.py"
)
kitchensink_core_app = create_example_fixture(HERE / "app-kitchensink-core.py")
kitchensink_express_app = create_example_fixture(HERE / "app-kitchensink-express.py")


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


def _check_multiple(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    letter = controller.InputRadioButtons(page, "letter")
    letter.set("C")

    top = controller.InputBookmarkButton(page, "bookmark_top")
    bottom = controller.InputBookmarkButton(page, "bookmark_bottom")
    top.expect_label("Bookmark (top)")
    bottom.expect_label("Bookmark (bottom)")

    # Either custom-id button triggers the bookmark via the reactive effect.
    bottom.click()
    expect(page).to_have_url(re.compile(r"letter"), timeout=10000)

    # The button ids are in session.bookmark.exclude, so they must NOT be
    # serialized into the bookmark URL -- only real inputs are.
    assert "bookmark_top" not in page.url
    assert "bookmark_bottom" not in page.url

    # Restoring still works.
    page.goto(page.url)
    controller.InputRadioButtons(page, "letter").expect_selected("C")


def test_bookmark_button_multiple_core(
    page: Page, multiple_core_app: ShinyAppProc
) -> None:
    _check_multiple(page, multiple_core_app)


def test_bookmark_button_multiple_express(
    page: Page, multiple_express_app: ShinyAppProc
) -> None:
    _check_multiple(page, multiple_express_app)


def _check_kitchensink(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    bookmark = controller.InputBookmarkButton(page)
    bookmark.expect_label("Save my state")
    bookmark.expect_width("300px")
    bookmark.expect_disabled(False)
    expect(bookmark.loc).to_have_attribute(
        "title", "Save these inputs and copy a shareable URL."
    )
    # icon= renders an inline SVG alongside the label.
    assert bookmark.loc.locator("svg").count() == 1


def test_bookmark_button_kitchensink_core(
    page: Page, kitchensink_core_app: ShinyAppProc
) -> None:
    _check_kitchensink(page, kitchensink_core_app)


def test_bookmark_button_kitchensink_express(
    page: Page, kitchensink_express_app: ShinyAppProc
) -> None:
    _check_kitchensink(page, kitchensink_express_app)
