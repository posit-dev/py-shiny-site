import pandas as pd
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Card 1"),
            ui.card_body("Content for card 1"),
            full_screen=True
        ),
        ui.card(
            ui.card_header("Card 2"),
            ui.card_body("Content for card 2"),
            full_screen=True
        ),
        width=1/2,
        height="300px"
    )
)


def server(input, output, session):
    @render.data_frame
    def sales_table():
        data = pd.DataFrame({
            "Product": ["Widget A", "Widget B", "Widget C", "Widget D", "Widget E"],
            "Region": ["North", "South", "East", "West", "North"],
            "Sales": [15_200, 12_800, 9_500, 11_300, 8_700],
            "Growth": ["+12%", "+8%", "+5%", "+10%", "+3%"]
        })

        if input.region_filter() != "All":
            data = data[data["Region"] == input.region_filter()]

        return data


app = App(app_ui, server)
