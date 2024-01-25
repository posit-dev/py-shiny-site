from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("show", "Show Notification")


@reactive.effect
@reactive.event(input.show)
def show_or_update_notification():
    ui.notification_show(
        f"You clicked the Show button {input.show()} times.",
        duration=None,
        # compare to what happens if you comment out the line below
        id="message",
    )
