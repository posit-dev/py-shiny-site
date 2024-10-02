from palmerpenguins import load_penguins
from shiny import App, reactive, render, ui

penguins = load_penguins()

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.input_action_button("update_selection", "Update selection"),
    ui.input_action_button("reset_selection", "Reset selection"),
    ui.h5("Current selection: ", {"class": "pt-2"}),
    ui.output_code("penguins_selection"),
    ui.output_data_frame("penguins_df"),
)

def server(input, output, session):

    @render.code
    def penguins_selection():
        return penguins_df.cell_selection()["rows"] # <<

    @render.data_frame
    def penguins_df():  # <<
        return render.DataTable(penguins, selection_mode="rows")  # <<

    @reactive.effect  
    @reactive.event(input.update_selection) 
    async def _():   # <<
        await penguins_df.update_cell_selection({"type": "row", "rows": [1, 2, 8]}) # <<
    
    @reactive.effect
    @reactive.event(input.reset_selection)
    async def _():  # <<
        await penguins_df.update_cell_selection({"type": "row", "rows": []})   # <<

app = App(app_ui, server)
