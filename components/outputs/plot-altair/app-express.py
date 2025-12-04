from palmerpenguins import load_penguins
import altair as alt
from shiny.express import input, ui
from shinywidgets import render_altair

dat = load_penguins().dropna()
species = dat["species"].unique().tolist()

ui.input_radio_buttons("species", "Species", species, inline=True)


@render_altair
def plot():
    sel = dat[dat["species"] == input.species()]

    plot = (
        alt.Chart(sel)
        .mark_bar()
        .encode(
            x=alt.X(
                "bill_length_mm",
                bin=alt.Bin(step=1),
                title="Bill Length (mm)",
            ),
            y=alt.Y("count()", title="Count"),
        )
    )

    return plot
