from shiny import render
from shiny.express import input, ui


ui.input_slider("slider", "Slider", min=0, max=100, value=[35, 65]) #<<


@render.text
def value():
    return f"{input.slider()}"
