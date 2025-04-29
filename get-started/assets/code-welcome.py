from palmerpenguins import load_penguins
from plotnine import aes, geom_histogram, ggplot, theme_minimal
from shiny.express import input, render, ui

all = load_penguins()
species = all["species"].unique().tolist()

ui.input_radio_buttons("species", "Species", species, inline=True)

@render.plot(height=300)
def plot():
    sel = all[all["species"] == input.species()]
    return (
        ggplot()
        + geom_histogram(all, aes(x="bill_length_mm"), fill="#C2C2C4", binwidth=1)
        + geom_histogram(sel, aes(x="bill_length_mm"), fill="#447099", binwidth=1)
        + theme_minimal()
    )
