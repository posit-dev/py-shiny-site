from shiny import render
from shiny.express import input, ui


ui.input_checkbox_group( #<<
    "checkbox_group", #<<
    "Checkbox group", #<<
    { #<<
        "a": "A", #<<
        "b": "B", #<<
        "c": "C", #<<
    }, #<<
) #<<


@render.text
def value():
    return ", ".join(input.checkbox_group())
