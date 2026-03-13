from shiny.express import input, render, ui

ui.input_code_editor("code", "Enter Python code:", "print('Hello, world!')") # <<

@render.code
def code_output():
    return input.code()
