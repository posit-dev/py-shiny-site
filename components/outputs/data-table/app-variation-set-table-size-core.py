from palmerpenguins import load_penguins
from shiny import App, render, ui

penguins = load_penguins()

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.output_data_frame("penguins_df"),
)


def server(input, output, session):
    @render.data_frame
    def penguins_df():
        return render.DataTable(penguins, width="300px", height="250px")  # <<


app = App(app_ui, server)
