from shiny import App, ui

app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card("Card 1"),
        ui.card("Card 2"),
        ui.card("Card 3"),
        col_widths=(2, 4, 6),
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server=server)
