# FIXME: Rewrite as an Express app
from palmerpenguins import load_penguins
from shiny import App, render, session, ui

penguins = load_penguins()

app_ui = ui.page_fluid(
    ui.input_numeric("n", "Number of rows to display", 20),
    ui.output_data_frame("penguins_df")
)

def server(input, output, session):
    @render.data_frame
    def penguins_df():
        data = penguins.head(input.n())
        return render.DataGrid(data, width = "300px", height = "250px") #<<

app = App(app_ui, server)
