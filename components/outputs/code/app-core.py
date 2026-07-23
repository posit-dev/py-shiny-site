from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.output_code("code_output"), # <<
)

def server(input, output, session):
    @render.code
    def code_output():
        return "def hello():\n    print('Hello, world!')"

app = App(app_ui, server)
