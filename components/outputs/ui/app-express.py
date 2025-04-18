from shiny.express import input, render, ui

ui.input_switch("show_slider", "Show slider", True)


@render.express  # <<
def ui_slider():  # <<
    if input.show_slider():
        value = input.slider() if "slider" in input else 5
        ui.input_slider("slider", "Choose a number", min=1, max=10, value=value)
