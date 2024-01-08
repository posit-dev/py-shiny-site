## file: app.py
import seaborn as sns
from palmerpenguins import load_penguins
from shiny import App, render, ui

app_ui = ui.page_fluid(
  ui.input_slider("n", "Number of bins", 1, 100, 20),
  ui.output_plot("plot"),  #<<
)


def server(input, output, session):
  @render.plot(
      alt="A Seaborn histogram on penguin body mass in grams."
  )  #<<
  def plot():  #<<
      penguins = load_penguins()
      ax = sns.histplot(data=penguins, x="body_mass_g", bins=input.n())
      ax.set_title("Palmer Penguins")
      ax.set_xlabel("Mass (g)")
      ax.set_ylabel("Count")
      return ax  #<<


app = App(app_ui, server, debug=True)
