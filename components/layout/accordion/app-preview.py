from shiny import App, ui

app_ui = ui.page_fluid(
    ui.accordion(
        ui.accordion_panel("Section A", "Contents for Section A"),
        ui.accordion_panel("Section B", "Contents for Section B"),
        ui.accordion_panel("Section C", "Contents for Section C"),
        id="acc",
    ),
    {"class": "vh-100 d-flex flex-column justify-content-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
