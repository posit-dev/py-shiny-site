from palmerpenguins import load_penguins
import altair as alt
from shiny import App, ui
from shinywidgets import render_altair, output_widget

dat = load_penguins().dropna()
species = dat["species"].unique().tolist()

app_ui = ui.page_fluid(
    ui.input_radio_buttons("species", "Species", species, inline=True),
    output_widget("plot"),
)


def server(input, output, session):
    @render_altair
    def plot():
        sel = dat[dat["species"] == input.species()]

        foreground = (
            alt.Chart(sel)
            .mark_bar()
            .encode(
                x=alt.X("bill_length_mm", bin=alt.Bin(step=1)),
                y=alt.Y("count()"),
            )
        )

        return foreground


app = App(app_ui, server)
