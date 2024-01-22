from shiny import reactive
from shiny.express import input, ui

types = ["default", "message", "warning", "error"]

ui.input_radio_buttons("type", "Notification Type", types, inline=True)
ui.input_action_button("show", "Show Notification")


@reactive.effect
@reactive.event(input.show)
def show_notification():
    type_txt = "notification" if input.type() == "default" else input.type()
    ui.notification_show(
        f"This {type_txt} will disappear after 2 seconds.",
        type=input.type(),
        duration=2,
    )
