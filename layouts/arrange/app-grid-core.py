from shiny import App, ui

app_ui = ui.page_fluid(
    ui.row(  # <<
        ui.column(12, ui.card("Card 1"))  # <<
    ),  # <<
    ui.row(  # <<
        ui.column(6, ui.card("Card 2")),  # <<
        ui.column(6, ui.card("Card 3")),  # <<
    ),  # <<
)


def server(input, output, session):
    return None


app = App(app_ui, server)
