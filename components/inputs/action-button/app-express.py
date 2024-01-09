from shiny import reactive, render
from shiny.express import input, ui


ui.input_action_button("action_button", "Action")  # <<


@render.text()
@reactive.event(input.action_button)
def counter():
    return f"{input.action_button()}"
