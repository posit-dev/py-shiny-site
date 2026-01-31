from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.output_code("code"),
)

def server(input, output, session):
    @render.code
    def code():
        return "print('Hello, world!')"

app = App(app_ui, server)
