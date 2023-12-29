# FIXME: Rewrite as an Express app
from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show Notification"),
)

def server(input, output, session):

    @reactive.Effect
    @reactive.event(input.show)
    def _():
        ui.notification_show(
            f"You clicked the Show button {input.show()} times.",
            duration=None,
            # compare to what happens if you comment out the line below #<<
            id="message" #<<
        )

app = App(app_ui, server)
