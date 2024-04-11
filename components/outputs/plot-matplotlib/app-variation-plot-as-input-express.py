import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny import render
from shiny.express import input, ui
from shiny.ui import output_code, output_plot

output_plot(
    "plot",
    click=True,  # <<
    dblclick=True,  # <<
    hover=True,  # <<
    brush=True,  # <<
)

"Click:"
output_code("clk", placeholder=True)
"Double Click:"
output_code("dblclk", placeholder=True)
"Hover:"
output_code("hvr", placeholder=True)
"Brush"
output_code("brsh", placeholder=True)


with ui.hold():
    # Note that this Express app uses `ui.hold()` so that we can
    # manually add the `output_plot()` and `output_code()` to the page.
    @render.plot(alt="A histogram")
    def plot():
        df = load_penguins()
        mass = df["body_mass_g"]
        bill = df["bill_length_mm"]

        plt.scatter(mass, bill)
        plt.xlabel("Mass (g)")
        plt.ylabel("Bill Length (mm)")
        plt.title("Penguin Mass vs Bill Length")

    @render.code
    def clk():
        return input.plot_click()

    @render.code
    def dblclk():
        return input.plot_dblclick()

    @render.code
    def hvr():
        return input.plot_hover()

    @render.code
    def brsh():
        return input.plot_brush()
