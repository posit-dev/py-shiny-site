from palmerpenguins import load_penguins
from shiny import render
from shiny.express import input, ui

penguins = load_penguins()

ui.h2("Palmer Penguins")


@render.ui()
def rows():
    rows = input.penguins_df_selected_rows()  # <<
    selected = ", ".join(str(i) for i in sorted(rows)) if rows else "None"
    return f"Rows selected: {selected}"


@render.data_frame
def penguins_df():
    return render.DataGrid(penguins, row_selection_mode="multiple")  # <<
