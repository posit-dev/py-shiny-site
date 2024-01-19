from shiny import App, ui

app_ui = ui.page_navbar(  # <<
    ui.nav_panel("A", "Page A content"),  # <<
    ui.nav_panel("B", "Page B content"),  # <<
    ui.nav_panel("C", "Page C content"),  # <<
    title="App with navbar",  # <<
    id="page",  # <<
)  # <<


def server(input, output, session):
    pass


app = App(app_ui, server)
