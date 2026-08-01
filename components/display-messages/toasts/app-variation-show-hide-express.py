from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("show", "Show toast")
ui.input_action_button("hide", "Hide toast")


@reactive.effect
@reactive.event(input.show)
def show_persistent_toast():
    ui.show_toast(
        ui.toast(
            "This toast stays until you hide it.",
            id="persistent_toast",  # <<
            duration_s=None,
            closable=False,
        )
    )


@reactive.effect
@reactive.event(input.hide)
def hide_persistent_toast():
    ui.hide_toast("persistent_toast")  # <<
