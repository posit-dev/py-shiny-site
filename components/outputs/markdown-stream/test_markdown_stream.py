from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")


def _check_markdown_stream_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # py-shiny has no MarkdownStream playwright controller yet, so assert on
    # the <shiny-markdown-stream> element directly.
    stream = page.locator("#md_stream")
    expect(stream).to_be_attached()
    expect(stream).not_to_contain_text("markdown stream")

    # Clicking the button streams the markdown chunks into the container,
    # rendered as HTML (heading + list), not raw markdown.
    controller.InputActionButton(page, "stream").click()
    expect(stream.locator("h2")).to_have_text(
        "Hello, markdown stream!", timeout=10000
    )
    expect(stream.locator("li")).to_have_count(2, timeout=10000)
    expect(stream).to_contain_text("one chunk at a time")


def test_markdown_stream_core_interaction(
    page: Page, core_app: ShinyAppProc
) -> None:
    _check_markdown_stream_interaction(page, core_app)


def test_markdown_stream_express_interaction(
    page: Page, express_app: ShinyAppProc
) -> None:
    _check_markdown_stream_interaction(page, express_app)
