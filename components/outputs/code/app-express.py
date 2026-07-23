from shiny.express import render

@render.code # <<
def code_output():
    return "def hello():\n    print('Hello, world!')"
