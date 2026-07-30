from shiny.express import input, render, ui

ui.input_code_editor("code", "Enter Python code:", "print('Hello, world!')", language="python")  # <<


@render.code
def value():
    return input.code()
