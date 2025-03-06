from shiny.express import input, render, ui

ui.input_selectize(  # <<
    "selectize",  # <<
    "Select an option below:",  # <<
    {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"},  # <<
)  # <<


@render.text
def value():
    return f"{input.selectize()}"
