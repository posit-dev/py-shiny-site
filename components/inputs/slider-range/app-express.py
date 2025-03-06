from shiny.express import input, render, ui

ui.input_slider("slider", "Slider", min=0, max=100, value=[35, 65])  # <<


@render.text
def value():
    return f"{input.slider()}"
