from palmerpenguins import load_penguins
from shiny import reactive
from shiny.express import input, render, ui

penguins = load_penguins()

ui.h2("Palmer Penguins")


ui.input_action_button("update_filters", "Update filters")
ui.input_action_button("reset_filters", "Reset filters")

ui.h5("Current filters: ", {"class": "pt-2"})


@render.code
def _():
    return penguins_df.filter()  # <<


@render.data_frame
def penguins_df():
    return render.DataGrid(penguins, filters=True)  # <<


@reactive.effect
@reactive.event(input.update_filters)
async def _():
    await penguins_df.update_filter(  # <<
        [  # <<
            # Set partial match # <<
            {"col": 0, "value": "Gen"},  # <<
            # Set min value # <<
            {"col": 2, "value": (50, None)},  # <<
            # Set max value # <<
            {"col": 3, "value": (None, 17)},  # <<
            # Set range # <<
            {"col": 4, "value": (220, 225)},  # <<
        ],  # <<
    )  # <<


@reactive.effect
@reactive.event(input.reset_filters)
async def _():
    await penguins_df.update_filter(None)  # <<
