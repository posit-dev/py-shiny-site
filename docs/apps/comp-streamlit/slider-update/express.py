from pathlib import Path

import pandas as pd
from plots import dist_plot, scatter_plot
from shiny import reactive, render, ui
from shiny.express import input, layout

infile = Path(__file__).parent / "penguins.csv"
df = pd.read_csv(infile)

with layout.sidebar():
    ui.input_slider("mass", "Mass", 2000, 8000, 6000)
    ui.input_checkbox("smoother", "Add Smoother")
    ui.input_action_button("reset", "Reset Slider")


@reactive.Effect
@reactive.event(input.reset)
def _():
    ui.update_slider("mass", value=6000)


@reactive.Calc
def filtered_data():
    filt_df = df.copy()
    filt_df = filt_df.loc[df["Body Mass (g)"] < input.mass()]
    return filt_df


with layout.card():

    @render.plot
    def scatter():
        return scatter_plot(filtered_data(), input.smoother())


with layout.card():

    @render.plot
    def mass_distribution():
        return dist_plot(filtered_data())
