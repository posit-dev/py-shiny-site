import plotly.express as px
from palmerpenguins import load_penguins
from shiny.express import input, ui
from shinywidgets import render_widget  # <<

penguins = load_penguins()

ui.input_slider("n", "Number of bins", 1, 100, 20)


@render_widget  # <<
def plot():  # <<
    scatterplot = px.histogram(
        data_frame=penguins,
        x="body_mass_g",
        nbins=input.n(),
    ).update_layout(
        title={"text": "Penguin Mass", "x": 0.5},
        yaxis_title="Count",
        xaxis_title="Body Mass (g)",
    )

    return scatterplot  # <<
