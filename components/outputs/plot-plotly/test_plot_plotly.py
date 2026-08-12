from pathlib import Path

from playwright.sync_api import Page, expect

from conftest import create_example_fixture
from shiny.playwright import controller
from shiny.run import ShinyAppProc

HERE = Path(__file__).parent

core_app = create_example_fixture(HERE / "app-core.py")
express_app = create_example_fixture(HERE / "app-express.py")

# Plotly attaches its chart asynchronously, after Shiny has delivered the widget
# output, so the chart can land well after page load -- and later still when the
# whole suite is competing for cores under xdist. Wait on the drawn chart itself
# with a generous bound rather than on Playwright's 5s default.
PLOT_TIMEOUT = 30 * 1000


def _check_plot_plotly_interaction(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    slider = controller.InputSlider(page, "n")
    slider.expect_value("20")

    # Assert on the chart Plotly draws inside the output container, not on the
    # container itself: an empty `#plot` is briefly "visible" while its
    # recalculating spinner holds the box open, so a container assertion passes
    # or fails purely on when it happens to run.
    expect(page.locator("#plot .js-plotly-plot")).to_be_visible(timeout=PLOT_TIMEOUT)
    # ...and on a drawn histogram trace, so a chart that attaches but renders
    # nothing (e.g. a widget that failed to receive its data) still fails.
    expect(page.locator("#plot g.trace.bars")).to_have_count(1, timeout=PLOT_TIMEOUT)


def test_plot_plotly_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
    _check_plot_plotly_interaction(page, core_app)


def test_plot_plotly_express_interaction(page: Page, express_app: ShinyAppProc) -> None:
    _check_plot_plotly_interaction(page, express_app)
