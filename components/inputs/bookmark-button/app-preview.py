from shiny import ui, App

app_ui = ui.page_fluid(
    ui.input_bookmark_button(),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
