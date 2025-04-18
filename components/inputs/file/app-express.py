from shiny import reactive
from shiny.express import input, render, ui

ui.input_file("f", "Pick a file, any file")  # <<
"Input file data:"


@render.text
def txt():
    return input.f()  # <<
