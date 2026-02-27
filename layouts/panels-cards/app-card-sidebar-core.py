import pandas as pd
from shiny import App, reactive, render, ui

# Create a small flower dataset
flowers = pd.DataFrame({
    "flower": ["Rose", "Tulip", "Daisy", "Orchid", "Lily", "Sunflower", "Violet", "Poppy"],
    "species": ["Rosa", "Tulipa", "Bellis", "Orchidaceae", "Lilium", "Helianthus", "Viola", "Papaver"],
    "color": ["Red", "Yellow", "White", "Purple", "Pink", "Yellow", "Purple", "Red"],
    "petal_length": [5.2, 3.8, 2.1, 6.3, 4.5, 8.1, 2.8, 3.5],
})

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Flower Data Explorer"),
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "color_filter",
                    "Filter by color",
                    ["All", "Red", "Yellow", "White", "Purple", "Pink"],
                ),
                ui.input_slider("rows", "Rows to show", 1, 8, 5),
                ui.input_action_button("reset", "Reset"),
            ),
            ui.card_body(
                ui.output_data_frame("flower_table"),
            ),
        ),
        full_screen=True,
        height="350px",
    )
)


def server(input, output, session):
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


app = App(app_ui, server)
