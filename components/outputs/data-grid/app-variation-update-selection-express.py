import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny import render, reactive
from shiny.express import input, ui
from shiny.ui import output_plot

def near_points(df, x, y, click):
    click_x = click["x"]
    click_y = click["y"]
    
    distances = ((df[x] - click_x) ** 2 + (df[y] - click_y) ** 2) ** 0.5

    closest_idx = distances.idxmin()
    return closest_idx

penguins = load_penguins().head(10)

output_plot(
    "plot",
    click=True
)

"Click on a point to highlight it in the table"

with ui.hold():
    @render.plot()
    def plot():
        plt.scatter(penguins["body_mass_g"], penguins["bill_length_mm"])
        plt.xlabel("Mass (g)")
        plt.ylabel("Bill Length (mm)")

@render.data_frame  # <<
def penguins_df(): # <<
    return render.DataGrid(penguins, selection_mode="rows") # <<

@reactive.effect # <<
async def _(): # <<
    point: float | None = input.plot_click() # <<
    if point is None: # <<
        await penguins_df.update_cell_selection({"type": "row", "rows": []}) # <<
    else: # <<
        row_id = near_points(penguins, "body_mass_g", "bill_length_mm", point) # <<
        await penguins_df.update_cell_selection({"type": "row", "rows": row_id}) # <<
