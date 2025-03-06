from shiny.express import input, render, ui

ui.input_switch("switch", "Switch", False)  # <<


@render.ui
def value():
    return input.switch()
