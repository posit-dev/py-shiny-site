from palmerpenguins import load_penguins
from shiny import reactive
from shiny.express import input, render, ui

penguins = load_penguins()

ui.h2("Palmer Penguins")

ui.input_action_button("update_selection", "Update row selection")
ui.input_action_button("reset_selection", "Reset row selection")

ui.h5("Current selection: ", {"class": "pt-2"})

@render.code
def _():  # <<
    return penguins_df.cell_selection()["rows"]  # <<

@render.data_frame
def penguins_df():  # <<
    return render.DataTable(penguins, selection_mode="rows")  # <<

@reactive.effect 
@reactive.event(input.update_selection)
async def _():  # <<
    await penguins_df.update_cell_selection({"type": "row", "rows": [1, 2, 8]})  # <<

@reactive.effect
@reactive.event(input.reset_selection)
async def _():  # <<
    await penguins_df.update_cell_selection({"type": "row", "rows": []})   # <<
