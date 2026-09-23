from palmerpenguins import load_penguins
from shiny import App, render, ui

penguins = load_penguins()[["species", "island", "bill_length_mm", "bill_depth_mm"]]

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.output_data_frame("penguins_df"),
)


def server(input, output, session):
    @render.data_frame
    def penguins_df():
        return render.DataGrid(penguins, selection_mode="rows")


app = App(app_ui, server)
