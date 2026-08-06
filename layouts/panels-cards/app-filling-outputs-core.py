from shiny import App, render, ui
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("A filling plot"),
        ui.card_body(ui.output_plot("plot")),
        height="250px",
        full_screen=True
    )
)


def server(input, output, session):
    @render.plot
    def plot():
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        return fig


app = App(app_ui, server)
