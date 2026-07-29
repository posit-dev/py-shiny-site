import pandas as pd
from shiny.express import input, render, ui
from shiny import reactive

# Create a small flower dataset
flowers = pd.DataFrame({
    "flower": ["Rose", "Tulip", "Daisy", "Orchid", "Lily", "Sunflower", "Violet", "Poppy"],
    "species": ["Rosa", "Tulipa", "Bellis", "Orchidaceae", "Lilium", "Helianthus", "Viola", "Papaver"],
    "color": ["Red", "Yellow", "White", "Purple", "Pink", "Yellow", "Purple", "Red"],
    "petal_length": [5.2, 3.8, 2.1, 6.3, 4.5, 8.1, 2.8, 3.5],
})

with ui.card(full_screen=True, height="350px"):
    ui.card_header("Flower Data Explorer")
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_select(
                "color_filter",
                "Filter by color",
                ["All", "Red", "Yellow", "White", "Purple", "Pink"],
            )
            ui.input_slider("rows", "Rows to show", 1, 8, 5)
            ui.input_action_button("reset", "Reset")
        with ui.card_body():

            @render.data_frame
            def flower_table():
                # Filter by color
                if input.color_filter() == "All":
                    df = flowers
                else:
                    df = flowers[flowers["color"] == input.color_filter()]

                # Limit rows
                return df.head(input.rows())

        @reactive.effect
        @reactive.event(input.reset)
        def _():
            ui.update_select("color_filter", selected="All")
            ui.update_slider("rows", value=5)
