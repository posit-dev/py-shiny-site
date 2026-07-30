from faicons import icon_svg

from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("show", "Show toast")


@reactive.effect
@reactive.event(input.show)
def show_message():
    ui.show_toast(  # <<
        ui.toast(
            "You have a new message!",
            header=ui.toast_header("Inbox", status="just now"),
            icon=icon_svg("envelope"),
            type="success",
            id="message_toast",
        )
    )
