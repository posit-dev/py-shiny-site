from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show Notification"),
)

def server(input, output, session):

    @reactive.Effect
    @reactive.event(input.show)
    def _():
        n=2
        ui.notification_show( #<<
            f"This will disappear after {n} seconds.", #<<
            duration=n #<<
        )

app = App(app_ui, server)
