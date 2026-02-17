from shiny.express import render, ui
import matplotlib.pyplot as plt

with ui.card(height="250px", full_screen=True):
    ui.card_header("A filling plot")

    @render.plot
    def plot():
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        return fig
