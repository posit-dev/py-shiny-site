from pathlib import Path

from playwright.sync_api import Page

from conftest import create_example_fixture
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")
detail_preview_app = create_example_fixture(HERE / "app-detail-preview.py")
preview_app = create_example_fixture(HERE / "app-preview.py")
kitchensink_core_app = create_example_fixture(HERE / "app-kitchensink-core.py")
kitchensink_express_app = create_example_fixture(HERE / "app-kitchensink-express.py")
variation_insert_core_app = create_example_fixture(
    HERE / "app-variation-insert-remove-core.py"
)
variation_insert_express_app = create_example_fixture(
    HERE / "app-variation-insert-remove-express.py"
)
variation_insert_preview_app = create_example_fixture(
    HERE / "app-variation-insert-remove-preview.py"
)
variation_update_core_app = create_example_fixture(
    HERE / "app-variation-update-panel-core.py"
)
variation_update_express_app = create_example_fixture(
    HERE / "app-variation-update-panel-express.py"
)
variation_update_preview_app = create_example_fixture(
    HERE / "app-variation-update-panel-preview.py"
)


def test_core_app_smoke(page: Page, core_app: ShinyAppProc, smoke_test) -> None:
    smoke_test(page, core_app)


def test_express_app_smoke(page: Page, express_app: ShinyAppProc, smoke_test) -> None:
    smoke_test(page, express_app)


def test_detail_preview_app_smoke(
    page: Page, detail_preview_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, detail_preview_app)


def test_preview_app_smoke(page: Page, preview_app: ShinyAppProc, smoke_test) -> None:
    smoke_test(page, preview_app)


def test_kitchensink_core_app_smoke(
    page: Page, kitchensink_core_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, kitchensink_core_app)


def test_kitchensink_express_app_smoke(
    page: Page, kitchensink_express_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, kitchensink_express_app)


def test_variation_insert_core_app_smoke(
    page: Page, variation_insert_core_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, variation_insert_core_app)


def test_variation_insert_express_app_smoke(
    page: Page, variation_insert_express_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, variation_insert_express_app)


def test_variation_insert_preview_app_smoke(
    page: Page, variation_insert_preview_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, variation_insert_preview_app)


def test_variation_update_core_app_smoke(
    page: Page, variation_update_core_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, variation_update_core_app)


def test_variation_update_express_app_smoke(
    page: Page, variation_update_express_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, variation_update_express_app)


def test_variation_update_preview_app_smoke(
    page: Page, variation_update_preview_app: ShinyAppProc, smoke_test
) -> None:
    smoke_test(page, variation_update_preview_app)
