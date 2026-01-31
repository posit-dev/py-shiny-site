from shiny import App, ui
import plotly.express as px

app_ui = ui.page_fixed(
    ui.card(  # <<
        ui.card_header(  # <<
            "Diamond Cut Distribution",  # <<
            class_="bg-dark",  # <<
        ),  # <<
        ui.card_body(  # <<
            "This card displays a histogram of diamond cuts from the diamonds dataset."  # <<
        ),  # <<
        max_height="400px",  # <<
        full_screen=True,  # <<
    )  # <<
)


def server(input, output, session):
    pass


app = App(app_ui, server)
