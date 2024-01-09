from shiny import App, reactive, ui
from pathlib import Path

appdir = Path(__file__).parent
app_ui = ui.page_fillable(
    ui.include_css(appdir / "styles.css"),
    ui.input_action_button("show", "Show Notification"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    ids: list[str] = []
    n: int = 0

    @reactive.Effect
    @reactive.event(input.show)
    def _():
        nonlocal ids
        nonlocal n
        # Save the ID for removal later
        id = ui.notification_show("Message " + str(n), duration=None)
        ids.append(id)
        n += 1

    @reactive.Effect
    @reactive.event(input.remove)
    def _():
        nonlocal ids
        if ids:
            ui.notification_remove(ids.pop())


app = App(app_ui, server)

## file: styles.css
# shiny-notification-panel { max-width: 100%; }
