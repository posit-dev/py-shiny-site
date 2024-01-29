import seaborn as sns
from palmerpenguins import load_penguins
from shiny import render
from shiny.express import input, ui

penguins = load_penguins()

ui.input_slider("n", "Number of bins", 1, 100, 20)


@render.plot(alt="A Seaborn histogram on penguin body mass in grams.")  # <<
def plot():  # <<
    ax = sns.histplot(data=penguins, x="body_mass_g", bins=input.n())  # <<
    ax.set_title("Palmer Penguins")
    ax.set_xlabel("Mass (g)")
    ax.set_ylabel("Count")
    return ax  # <<
