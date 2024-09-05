from palmerpenguins import load_penguins
from shiny import reactive
from shiny.express import input, render, ui

penguins = load_penguins()

ui.h2("Palmer Penguins")


ui.input_action_button("update_sorting", "Update sorting")
ui.input_action_button("reset_sorting", "Reset sorting")

ui.h5("Current sorting: ", {"class": "pt-2"})


@render.code
def _():
    return penguins_df.sort()  # <<


@render.data_frame
def penguins_df():
    return render.DataTable(penguins)


@reactive.effect
@reactive.event(input.update_sorting)
async def _():
    await penguins_df.update_sort(  # <<
        [1, 0, {"col": 6, "desc": False}, 7],  # <<
    )  # <<


@reactive.effect
@reactive.event(input.reset_sorting)
async def _():
    await penguins_df.update_sort([])  # <<
