from shiny import render
from shiny.express import input, ui


ui.input_text("text", "Text input", "Enter text...") #<<


@render.text
def value():
    return input.text()

