from shiny.express import input, render, ui

ui.input_slider("slider", "Slider", 0, 100, 50)  # <<


@render.text
def value():
    return f"{input.slider()}"
