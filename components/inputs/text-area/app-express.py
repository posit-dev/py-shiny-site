from shiny.express import input, render, ui

ui.input_text_area("textarea", "Text input", "Hello World")  # <<


@render.text
def value():
    return input.textarea()
