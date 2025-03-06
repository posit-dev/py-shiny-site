from shiny.express import input, render, ui

ui.input_checkbox("checkbox", "Checkbox", False)  # <<


@render.ui
def value():
    return input.checkbox()
