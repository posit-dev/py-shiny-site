from shiny import App, render, ui
import pandas as pd

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.card(
            ui.card_header(
                "Sales Data",
                ui.toolbar(
                    ui.toolbar_input_select(
                        id="region_filter",
                        label="Region",
                        choices=["All", "North", "South", "East", "West"],
                        selected="All"
                    )
                )
            ),
            ui.card_body(
                ui.output_data_frame("sales_table")
            ),
            full_screen=True
        ),
        ui.card(
            ui.card_header("Key Insights"),
            ui.card_body(
                ui.markdown("""
                **Performance Summary**

                - Sales increased by 96% over 6 months
                - April showed a temporary dip
                - Strong recovery in May and June
                - Current trajectory suggests continued growth

                *Data updated: June 2024*
                """)
            ),
            full_screen=True
        )
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
