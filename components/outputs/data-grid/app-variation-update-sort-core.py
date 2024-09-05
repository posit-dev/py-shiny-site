from palmerpenguins import load_penguins
from shiny import App, reactive, render, ui

penguins = load_penguins()

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.input_action_button("update_sorting", "Update sorting"),
    ui.input_action_button("reset_sorting", "Reset sorting"),
    ui.h5("Current sorting: ", {"class": "pt-2"}),
    ui.output_code("penguins_sort"),
    ui.output_data_frame("penguins_df"),
)


def server(input, output, session):

    @render.code
    def penguins_sort():
        return penguins_df.sort()  # <<

    @render.data_frame
    def penguins_df():
        return render.DataGrid(penguins)

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


app = App(app_ui, server)
