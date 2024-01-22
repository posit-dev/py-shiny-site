from shiny import App, reactive, ui

types = ["default", "message", "warning", "error"]

app_ui = ui.page_fluid(
    ui.input_radio_buttons("type", "Notification Type", types, inline=True),
    ui.input_action_button("show", "Show Notification"),
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        type_txt = "notification" if input.type() == "default" else input.type()

        ui.notification_show(
            f"This {type_txt} will disappear after 2 seconds.",
            type=input.type(),
            duration=2,
        )


app = App(app_ui, server)
