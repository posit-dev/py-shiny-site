from shiny.express import input, render, ui
import pandas as pd

with ui.layout_column_wrap():
    with ui.card(full_screen=True):
        with ui.card_header():
            "Sales Data"
            with ui.toolbar():
                ui.toolbar_input_select(
                    id="region_filter",
                    label="Region",
                    choices=["All", "North", "South", "East", "West"],
                    selected="All"
                )

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

    with ui.card(full_screen=True):
        ui.card_header("Key Insights")
        ui.markdown("""
        **Performance Summary**

        - Sales increased by 96% over 6 months
        - April showed a temporary dip
        - Strong recovery in May and June
        - Current trajectory suggests continued growth

        *Data updated: June 2024*
        """)
