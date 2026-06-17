from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_code_editor("code", "Enter Python code:", "print('Hello, world!')"), # <<
    ui.output_code("code_output"),
)

def server(input, output, session):
    @render.code
    def code_output():
        return input.code()

app = App(app_ui, server)
