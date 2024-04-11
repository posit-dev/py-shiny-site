from htmltools import css
from shiny import App, ui

app_ui = ui.page_fillable(
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
    style=css(
        background_image="url(https://unsplash.com/photos/XKXGghL7GQc/download?force=true&w=1920)",
        background_repeat="no-repeat",
        background_size="cover",
        background_position="center bottom",
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
