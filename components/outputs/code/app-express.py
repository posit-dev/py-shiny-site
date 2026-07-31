from shiny.express import input, render, ui

ui.input_text("message", "Message", "Hello Shiny")


@render.code  # <<
def code():
    return f'print("{input.message()}")'
