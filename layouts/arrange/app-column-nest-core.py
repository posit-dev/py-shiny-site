from shiny import App, ui

app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card("Card 1"),
        ui.card(
            "Card 2",
            ui.layout_columns(
                ui.card("Card 2.1"),
                ui.card("Card 2.2"),
                width=1 / 2,
            ),
        ),
        col_widths=(4, 8),
    ),
)


def server(input, output, session):
    return None


app = App(app_ui, server)
