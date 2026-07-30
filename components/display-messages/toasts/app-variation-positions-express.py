from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("top_left", "Top left")
ui.input_action_button("top_center", "Top center")
ui.input_action_button("middle_center", "Middle center")
ui.input_action_button("bottom_right", "Bottom right")


@reactive.effect
@reactive.event(input.top_left)
def show_top_left():
    ui.show_toast(
        ui.toast(
            "Top left position",
            position="top-left",  # <<
            id="toast_top_left",
        )
    )


@reactive.effect
@reactive.event(input.top_center)
def show_top_center():
    ui.show_toast(
        ui.toast(
            "Top center position",
            position="top-center",
            id="toast_top_center",
        )
    )


@reactive.effect
@reactive.event(input.middle_center)
def show_middle_center():
    ui.show_toast(
        ui.toast(
            "Middle center position",
            position="middle-center",
            id="toast_middle_center",
        )
    )


@reactive.effect
@reactive.event(input.bottom_right)
def show_bottom_right():
    ui.show_toast(
        ui.toast(
            "Bottom right position",
            position="bottom-right",
            id="toast_bottom_right",
        )
    )
