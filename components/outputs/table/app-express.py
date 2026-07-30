import pandas as pd

from shiny.express import input, render, ui

df = pd.DataFrame(
    {
        "Model": ["Mazda RX4", "Datsun 710", "Merc 240D", "Fiat 128", "Volvo 142E"],
        "MPG": [21.0, 22.8, 24.4, 32.4, 21.4],
        "Cylinders": [6, 4, 4, 4, 4],
        "Horsepower": [110, 93, 62, 66, 109],
    }
)

ui.input_slider("rows", "Rows to display", min=1, max=5, value=3)


@render.table  # <<
def table():
    return df.head(input.rows())
