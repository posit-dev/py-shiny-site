import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.output_plot(
        "plot",
        click=True,  # <<
        dblclick=True,  # <<
        hover=True,  # <<
        brush=True,  # <<
    ),
    "Click:",
    ui.output_code("clk"),
    "Double Click:",
    ui.output_code("dblclk"),
    "Hover:",
    ui.output_code("hvr"),
    "Brush",
    ui.output_code("brsh"),
)


def server(input, output, session):
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


app = App(app_ui, server, debug=True)
