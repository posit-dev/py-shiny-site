from shiny import render
from shiny.express import input, ui

ui.input_checkbox("checkbox", "Checkbox", False) #<<


@render.ui
def value():
    return input.checkbox()
