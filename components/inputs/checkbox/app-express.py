from shiny import render
from shiny.express import input, ui


ui.page_opts(full_width=True)

ui.input_checkbox("checkbox", "Checkbox", False)


@render.ui
def value():
    return input.checkbox()
