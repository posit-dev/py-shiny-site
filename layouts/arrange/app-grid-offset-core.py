from shiny import App, ui

app_ui = ui.page_fluid(
    ui.row(
        ui.column(4, ui.card("Card 1")),
        ui.column(4, ui.card("Card 2"), offset=4),  # <<
    ),
    ui.row(
        ui.column(4, ui.card("Card 3"), offset=4)  # <<
    ),
    ui.row(
        ui.column(4, ui.card("Card 4")),  # <<
        ui.column(4, ui.card("Card 5"), offset=4),  # <<
    ),
)


def server(input, output, session):
    return None


app = App(app_ui, server)
