from shiny import App, ui

app_ui = ui.page_fillable(
    ui.layout_column_wrap(  # <<
        ui.card("Card 1"),
        ui.card("Card 2"),
        ui.card("Card 3"),
        ui.card("Card 4"),
        width="300px",  # <<
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server=server)
