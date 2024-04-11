from shiny import App, ui

app_ui = ui.page_fillable(
    ui.card(  # <<
        ui.card_header("Card with sidebar"),
        ui.layout_sidebar(  # <<
            ui.sidebar("Sidebar", bg="#f8f8f8"),  # <<
            "Card content",  # <<
        ),  # <<
    )  # <<
)


def server(input, output, session):
    pass


app = App(app_ui, server)
