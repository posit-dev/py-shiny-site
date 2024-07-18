from palmerpenguins import load_penguins
from shiny.express import render, ui

penguins = load_penguins()

ui.h2("Palmer Penguins")


@render.data_frame
def penguins_df():
    return render.DataGrid(penguins, width="300px", height="250px")  # <<
