import plotly.express as px
from palmerpenguins import load_penguins
from shiny import App, ui
from shinywidgets import output_widget, render_widget  # <<

penguins = load_penguins()

app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of bins", 1, 100, 20),
    output_widget("plot"),  # <<
)


def server(input, output, session):
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


app = App(app_ui, server)
