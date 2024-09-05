from palmerpenguins import load_penguins
from shiny.express import render, ui

penguins = load_penguins()

ui.h2("Palmer Penguins")

"The shape of the selected data frame is :"


@render.code
def penguins_shape():
    data = penguins_df.data_view(selected=True)  # <<
    return data.shape


@render.data_frame
def penguins_df():
    return render.DataTable(penguins, selection_mode="rows")
