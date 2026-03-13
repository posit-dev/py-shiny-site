## file: app.py
from shiny import ui, reactive, App
from pathlib import Path

appdir = Path(__file__).parent
app_ui = ui.page_fillable(
    ui.include_css(appdir / "styles.css"),
    ui.input_action_button("show", "Show Toast"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)

def server(input, output, session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        ui.show_toast("This is a toast notification!")

app = App(app_ui, server)

## file: styles.css
# shiny-notification-panel { max-width: 100%; }
