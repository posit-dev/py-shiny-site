from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("A long, scrolling, description"),
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. " * 15,
        max_height="250px",
        full_screen=True
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
