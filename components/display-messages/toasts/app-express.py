from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("show", "Show toast")

@reactive.effect
@reactive.event(input.show)
def _():
    ui.show_toast("Hello! This is a toast message.") # <<
