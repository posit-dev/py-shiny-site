from shiny import App, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Card 1"),
            ui.card_body("Content for card 1"),
            full_screen=True
        ),
        ui.card(
            ui.card_header("Card 2"),
            ui.card_body("Content for card 2"),
            full_screen=True
        ),
        width=1/2,
        height="300px"
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
