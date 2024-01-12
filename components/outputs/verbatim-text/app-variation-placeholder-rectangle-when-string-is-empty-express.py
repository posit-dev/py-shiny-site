from shiny import render
from shiny.express import input, suspend_display, ui

ui.input_text("Text", "Enter Text", "")
ui.output_text_verbatim("text", placeholder=True)  # <<

with suspend_display():  # <<

    @render.text  # <<
    def text():
        return input.Text()
