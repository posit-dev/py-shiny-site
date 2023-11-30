from pathlib import Path

import pandas as pd
from plots import dist_plot, scatter_plot
from shiny import App, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("mass", "Mass", 2000, 8000, 6000),
        ui.input_checkbox("smoother", "Add Smoother"),
        ui.input_action_button("reset", "Reset Slider"),
    ),
    ui.card(ui.output_plot(id="scatter")),
    ui.card(ui.output_plot(id="mass_distribution")),
)


def server(input, output, session):
    infile = Path(__file__).parent / "penguins.csv"
    df = pd.read_csv(infile)

    @reactive.Calc
    def filtered_data():
        filt_df = df.copy()
        filt_df = filt_df.loc[df["Body Mass (g)"] < input.mass()]
        return filt_df

    @output
    @render.plot
    def mass_distribution():
        return dist_plot(filtered_data())

    @output
    @render.plot
    def scatter():
        return scatter_plot(filtered_data(), input.smoother())


app = App(app_ui, server)
from pathlib import Path

import pandas as pd
from plots import dist_plot, scatter_plot
from shiny import App, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("mass", "Mass", 2000, 8000, 6000),
        ui.input_checkbox("smoother", "Add Smoother"),
        ui.input_action_button("reset", "Reset Slider"),
    ),
    ui.card(ui.output_plot(id="scatter")),
    ui.card(ui.output_plot(id="mass_distribution")),
)


def server(input, output, session):
    infile = Path(__file__).parent / "penguins.csv"
    df = pd.read_csv(infile)

    @reactive.Calc
    def filtered_data():
        filt_df = df.copy()
        filt_df = filt_df.loc[df["Body Mass (g)"] < input.mass()]
        return filt_df

    @render.plot
    def mass_distribution():
        return dist_plot(filtered_data())

    @render.plot
    def scatter():
        return scatter_plot(filtered_data(), input.smoother())

    @reactive.Effect
    @reactive.event(input.reset)
    def _():
        ui.update_slider("mass", value=6000)


app = App(app_ui, server)
