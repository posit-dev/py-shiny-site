from shiny import reactive, render
from shiny.express import input, ui


ui.input_action_link("action_link", "Action") #<<


@render.text()
@reactive.event(input.action_link)
def counter():
    return f"{input.action_link()}"
