from palmerpenguins import load_penguins
from shiny import App, render, ui

penguins = load_penguins()

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.output_ui("rows"),
    ui.output_data_frame("penguins_df"),
)


def server(input, output, session):
    @render.data_frame
    def penguins_df():
        return render.DataTable(penguins, row_selection_mode="single")  # <<

    @render.ui
    def rows():
        rows = input.penguins_df_selected_rows()  # <<
        selected = ", ".join(str(i) for i in sorted(rows)) if rows else "None"
        return f"Rows selected: {selected}"


app = App(app_ui, server)
