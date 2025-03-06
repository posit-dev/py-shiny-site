from shiny.express import input, render, ui

ui.input_text("Text", "Enter text", "Hello Shiny")


@render.text  # <<
def text():
    return input.Text()
