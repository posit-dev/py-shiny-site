from palmerpenguins import load_penguins
from shiny import App, render, ui

penguins = load_penguins()

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    "The shape of the selected data frame is :",
    ui.output_code("penguins_shape"),
    ui.output_data_frame("penguins_df"),
)


def server(input, output, session):
    @render.data_frame
    def penguins_df():
        return render.DataGrid(penguins, selection_mode="rows")

    @render.code
    def penguins_shape():
        data = penguins_df.data_view(selected=True)  # <<
        return data.shape


app = App(app_ui, server)
