from shiny import App, ui

app_ui = ui.page_fillable(
    ui.layout_columns(  # <<
        ui.card(  # <<
            ui.card_header("Card 1 header"),
            ui.p("Card 1 body"),
            ui.input_slider("slider", "Slider", 0, 10, 5),
        ),  # <<
        ui.card(  # <<
            ui.card_header("Card 2 header"),
            ui.p("Card 2 body"),
            ui.input_text("text", "Add text", ""),
        ),  # <<
    )  # <<
)


def server(input, output, session):
    pass


app = App(app_ui, server)
