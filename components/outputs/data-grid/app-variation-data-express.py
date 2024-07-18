from palmerpenguins import load_penguins
from shiny import render
from shiny.express import ui

penguins = load_penguins()

ui.h2("Palmer Penguins")

"The shape of the data frame is :"


@render.code
def penguins_shape():
    data = penguins_df.data()  # <<
    return data.shape


@render.data_frame
def penguins_df():
    return render.DataGrid(penguins)
