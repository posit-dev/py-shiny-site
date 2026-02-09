from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Project Overview",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="view_details",
                    label="View Details",
                    icon=icon_svg("eye"),
                ),
                ui.toolbar_input_button(
                    id="download",
                    label="Download",
                    icon=icon_svg("download"),
                ),
                align="right",
            ),
            class_="bg-primary text-white"
        ),
        ui.card_body(
            ui.p("This project analyzes customer data to identify trends and patterns."),
            ui.p("Key metrics include sales volume, customer retention, and market growth."),
        ),
        full_screen=True
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
