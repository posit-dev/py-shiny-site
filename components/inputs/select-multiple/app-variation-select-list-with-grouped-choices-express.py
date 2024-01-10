from shiny import render
from shiny.express import input, ui


ui.input_select( #<<
    "select", #<<
    "Select options below:", #<<
    {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"}, #<<
    multiple=True #<<
) #<<


@render.text
def value():
    return f"{input.select()}"
