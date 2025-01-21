from pathlib import Path

import pandas as pd
from shiny import render
from shiny.express import input, ui
from shinywidgets import render_widget

from data import create_merged_data, load_merged_data
from map import plot_choropleth

merged_data = load_merged_data(
    counties_file='data/counties.csv',
    fips_file='data/fips.csv',
    output_file="data/merged_data.csv",
).dropna() # we will drop rows with missing values for now

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

@render_widget
def map():
    choropleth = plot_choropleth(
        dataframe=merged_data,
        color_column='white',
        title='% White',
    )

    return choropleth
