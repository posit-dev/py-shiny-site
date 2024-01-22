import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny import render
from shiny.express import input, suspend_display, ui

ui.output_plot(
    "plot",
    click=True,  # <<
    dblclick=True,  # <<
    hover=True,  # <<
    brush=True,  # <<
)

"Click:"
ui.output_text_verbatim("clk", placeholder=True)
"Double Click:"
ui.output_text_verbatim("dblclk", placeholder=True)
"Hover:"
ui.output_text_verbatim("hvr", placeholder=True)
"Brush"
ui.output_text_verbatim("brsh", placeholder=True)


with suspend_display():
    # Note that this Express app uses `suspend_display()` so that we can
    # manually add the `ui.output_plot()` and others to the page.

    @render.plot(alt="A histogram")
    def plot():
        df = load_penguins()
        mass = df["body_mass_g"]
        bill = df["bill_length_mm"]

        plt.scatter(mass, bill)
        plt.xlabel("Mass (g)")
        plt.ylabel("Bill Length (mm)")
        plt.title("Penguin Mass vs Bill Length")

    @render.text
    def clk():
        return input.plot_click()

    @render.text
    def dblclk():
        return input.plot_dblclick()

    @render.text
    def hvr():
        return input.plot_hover()

    @render.text
    def brsh():
        return input.plot_brush()
