from shiny.express import ui
import plotly.express as px

with ui.card(max_height="400px", full_screen=True):  # <<
    ui.card_header(  # <<
        "Diamond Cut Distribution",  # <<
        class_="bg-dark",  # <<
    )  # <<
    "This card displays a histogram of diamond cuts from the diamonds dataset."  # <<
