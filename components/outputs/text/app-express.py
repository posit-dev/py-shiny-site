from shiny import render
from shiny.express import input, ui

ui.input_text("Text", "Enter text", "Hello Shiny")
"You entered:"


@render.text  # <<
def text():
    return input.Text()
