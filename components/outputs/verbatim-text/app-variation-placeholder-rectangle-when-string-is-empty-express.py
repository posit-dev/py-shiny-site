from shiny.express import input, render, ui

ui.input_text("Text", "Enter Text", "")


@render.code(placeholder=True)  # <<
def text():
    return input.Text()
