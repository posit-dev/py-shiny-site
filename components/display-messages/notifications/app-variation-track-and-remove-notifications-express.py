# FIXME: Rewrite as an Express app
from shiny import App, reactive, ui

    app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show Notification"),
    ui.input_action_button("remove", "Remove Notification"),
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
            ui.notification_remove(ids.pop()) #<<

app = App(app_ui, server)
