from shiny import render
from shiny.express import input, ui


ui.input_switch("switch", "Switch", False)  # <<


@render.ui
def value():
    return input.switch()
