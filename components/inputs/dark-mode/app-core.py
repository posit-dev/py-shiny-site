from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_dark_mode() # <<
)

def server(input, output, session):
    pass

app = App(app_ui, server)
