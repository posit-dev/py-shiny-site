from pathlib import Path

import pandas as pd
from shiny import render
from shiny.express import input, ui

csv_file = Path(__file__).parent.parent / "data" / "counties.csv"
df = pd.read_csv(csv_file)

ui.page_opts(title="Census Visualization", fillable=True)

with ui.sidebar(bg="#f8f8f8"):
    ui.help_text("Create demographic maps with information from the 2020 US Census.")
    ui.input_select(
        "var",
        "Choose a variable to display",
        [
            "Percent White",
            "Percent Black",
            "Percent Hispanic",
            "Percent Asian",
        ],
        selected="Percent White",
    )

    ui.input_slider("range", "Range of interest:", min=10, max=100, value=[0, 100])

@render.text
def text_output():
    return input.var()

@render.code
def text_verbatim_code():
    return f"{input.range()[0]}, {input.range()[1]}"
