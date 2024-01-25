from shiny import render
from shiny.express import input, ui


(ui.input_text_area("textarea", "Text input", "Hello World"),)  # <<


@render.text
def value():
    return input.textarea()
