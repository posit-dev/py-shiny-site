from shiny.express import input, render, ui

ui.input_numeric("numeric", "Numeric input", 1, min=1, max=10)  # <<


@render.text
def value():
    return input.numeric()
