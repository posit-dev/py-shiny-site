import pandas as pd

from shiny import App, render, ui

df = pd.DataFrame(
    {
        "Model": ["Mazda RX4", "Datsun 710", "Merc 240D", "Fiat 128", "Volvo 142E"],
        "MPG": [21.0, 22.8, 24.4, 32.4, 21.4],
        "Cylinders": [6, 4, 4, 4, 4],
        "Horsepower": [110, 93, 62, 66, 109],
    }
)

app_ui = ui.page_fluid(
    ui.input_slider("rows", "Rows to display", min=1, max=5, value=3),
    ui.output_table("table"),  # <<
)


def server(input, output, session):
    @render.table  # <<
    def table():
        return df.head(input.rows())


app = App(app_ui, server)
