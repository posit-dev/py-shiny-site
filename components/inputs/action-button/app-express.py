from shiny import reactive, render
from shiny.express import input, ui


ui.page_opts(full_width=True)

ui.input_action_button("action_button", "Action")


@render.text()
@reactive.event(input.action_button)
def counter():
    return f"{input.action_button()}"
