from pathlib import Path

import pandas as pd
from palmerpenguins import load_penguins
from plots import dist_plot, scatter_plot
from shiny import reactive, render
from shiny.express import input, ui

df = load_penguins()

with ui.sidebar():
    ui.input_slider("mass", "Mass", 2000, 8000, 6000)
    ui.input_checkbox("smoother", "Add Smoother")
    ui.input_action_button("reset", "Reset Slider")


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("mass", value=6000)


@reactive.calc
def filtered_data():
    filt_df = df.copy()
    filt_df = filt_df.loc[df["body_mass_g"] < input.mass()]
    return filt_df


with ui.card():

    @render.plot
    def scatter():
        return scatter_plot(filtered_data(), input.smoother())


with ui.card():

    @render.plot
    def mass_distribution():
        return dist_plot(filtered_data())
