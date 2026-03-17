from faicons import icon_svg
from shiny.express import ui

with ui.card(full_screen=True):
    with ui.card_header(class_="bg-primary text-white"):
        "Project Overview"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(
                id="view_details",
                label="View Details",
                icon=icon_svg("eye"),
            )
            ui.toolbar_input_button(
                id="download",
                label="Download",
                icon=icon_svg("download"),
            )

    ui.p("This project analyzes customer data to identify trends and patterns.")
    ui.p("Key metrics include sales volume, customer retention, and market growth.")
