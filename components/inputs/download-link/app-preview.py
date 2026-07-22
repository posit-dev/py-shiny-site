from shiny import ui, App

app_ui = ui.page_fluid(
    ui.download_link("download", "Download"),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
