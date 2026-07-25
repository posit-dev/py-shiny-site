import re
from datetime import date
from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")

EXPECTED_CSV = "name,value\nAlice,100\nBob,200\n"


def _check_download_link(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    link = controller.DownloadLink(page, "download_data")
    expect(link.loc).to_contain_text("Download CSV")
    # The link is disabled until the session registers the download handler.
    expect(link.loc).not_to_have_class(re.compile(r"\bdisabled\b"))

    with page.expect_download() as download_info:
        link.loc.click()
    download = download_info.value

    assert download.suggested_filename == f"data-{date.today().isoformat()}.csv"
    assert Path(download.path()).read_text() == EXPECTED_CSV


def test_download_link_core(page: Page, core_app: ShinyAppProc) -> None:
    _check_download_link(page, core_app)


def test_download_link_express(page: Page, express_app: ShinyAppProc) -> None:
    _check_download_link(page, express_app)
