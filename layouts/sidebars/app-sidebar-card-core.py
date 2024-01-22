from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(  # <<
        ui.layout_sidebar(  # <<
            ui.sidebar("Sidebar", bg="#f8f8f8"),  # <<
            "Card content",
        ),  # <<
    )  # <<
)


def server(input, output, session):
    pass


app = App(app_ui, server)
