from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show Warning"),
)

def server(input, output, session):

    @reactive.Effect
    @reactive.event(input.show)
    def _():
        n=2
        ui.notification_show(
            f"This will disappear after {n} seconds.",
            duration=n,
            type="warning" #<<
        )

app = App(app_ui, server)
