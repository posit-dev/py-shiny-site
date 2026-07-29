from shiny import App, ui

app_ui = ui.page_fluid(
    ui.accordion(
        ui.accordion_panel("Section A", "Some narrative for section A"),
        ui.accordion_panel("Section B", "Some narrative for section B"),
        ui.accordion_panel("Section C", "Some narrative for section C"),
        id="acc",
    ),
    {"class": "vh-100 d-flex flex-column justify-content-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
