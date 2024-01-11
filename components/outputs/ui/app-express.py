from shiny import render
from shiny.express import input, ui

ui.input_switch("show_slider", "Show slider", True)


@render.ui  # <<
def uiElement():  # <<
    if input.show_slider():
        value = input.slider() if "slider" in input else 5
        return ui.input_slider("slider", "Choose a number", min=1, max=10, value=value)
