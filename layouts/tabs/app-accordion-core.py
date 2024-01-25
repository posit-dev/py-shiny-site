from shiny import App, ui

app_ui = ui.page_fluid(
    ui.accordion(  # <<
        ui.accordion_panel("Section A", "Section A content"),  # <<
        ui.accordion_panel("Section B", "Section B content"),  # <<
        ui.accordion_panel("Section C", "Section C content"),  # <<
        ui.accordion_panel("Section D", "Section D content"),  # <<
        ui.accordion_panel("Section E", "Section E content"),  # <<
        id="acc",  # <<
        open="Section A",  # <<
    ),  # <<
)


def server(input, output, session):
    pass


app = App(app_ui, server)
