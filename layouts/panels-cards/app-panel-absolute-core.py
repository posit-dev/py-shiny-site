from shiny import App, ui

app_ui = ui.page_fluid(
    ui.panel_absolute(  # <<
        ui.panel_well(
            ui.panel_title("Draggable panel"),
            "Move this panel anywhere you want.",
        ),
        width="300px",  # <<
        right="50px",  # <<
        top="50px",  # <<
        draggable=True,  # <<
    ),  # <<
)


def server(input, output, session):
    pass


app = App(app_ui, server)
