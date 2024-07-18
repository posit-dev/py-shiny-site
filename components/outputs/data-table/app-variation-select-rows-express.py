from palmerpenguins import load_penguins
from shiny.express import input, render, ui

penguins = load_penguins()

ui.h2("Palmer Penguins")


@render.ui
def rows():
    rows = penguins_df.cell_selection()["rows"]  # <<
    selected = ", ".join(str(i) for i in sorted(rows)) if rows else "None"
    return f"Rows selected: {selected}"


@render.data_frame
def penguins_df():
    return render.DataTable(penguins, selection_mode="rows")  # <<
