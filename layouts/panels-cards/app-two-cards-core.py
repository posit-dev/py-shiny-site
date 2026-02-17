from shiny import App, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Card 1"),
            ui.p("Card 1 body"),
            ui.input_slider("slider", "Slider", 0, 10, 5),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Card 2"),
            ui.p("Card 2 body"),
            ui.input_text("text", "Add text", ""),
            full_screen=True,
        ),
        width=1/2,
        height="300px",
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
