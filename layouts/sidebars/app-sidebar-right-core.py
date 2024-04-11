from shiny import App, ui

app_ui = ui.page_sidebar(  # <<
    ui.sidebar("Sidebar", position="right", bg="#f8f8f8"),  # <<
    "Main content",
)  # <<


def server(input, output, session):
    pass


app = App(app_ui, server)
