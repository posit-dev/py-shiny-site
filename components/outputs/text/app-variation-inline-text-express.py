from shiny import render
from shiny.express import input, suspend_display, ui

ui.input_text("Text", "Enter text", "Hello Shiny")
"You entered:"
ui.output_text("text", inline=True)  # <<


@suspend_display()  # <<
@render.text  # <<
def text():
    return input.Text()
