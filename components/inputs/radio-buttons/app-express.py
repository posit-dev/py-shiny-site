from shiny import render
from shiny.express import input, ui


ui.input_radio_buttons( #<<
    "radio", #<<
    "Radio buttons", #<<
    {"1": "Option 1", "2": "Option 2", "3": "Option 3"}, #<<
) #<<


@render.ui
def value():
    return input.radio()
