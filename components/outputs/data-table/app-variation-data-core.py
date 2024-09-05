from palmerpenguins import load_penguins
from shiny import App, render, ui

penguins = load_penguins()

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    "The shape of the data frame is :",
    ui.output_code("penguins_shape"),
    ui.output_data_frame("penguins_df"),
)


def server(input, output, session):
    @render.data_frame
    def penguins_df():
        return render.DataTable(penguins)

    @render.code
    def penguins_shape():
        data = penguins_df.data()  # <<
        return data.shape


app = App(app_ui, server)
