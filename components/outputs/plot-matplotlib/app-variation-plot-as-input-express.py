# FIXME: Rewrite as an Express app
import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.output_plot(
        "plot", 
        click=True, #<<
        dblclick=True, #<<
        hover=True, #<<
        brush=True #<<
    ),
    "Click:",
    ui.output_text_verbatim("clk", placeholder=True),
    "Double Click:",
    ui.output_text_verbatim("dblclk", placeholder=True),
    "Hover:",
    ui.output_text_verbatim("hvr", placeholder=True),
    "Brush",
    ui.output_text_verbatim("brsh", placeholder=True),
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
        
app = App(app_ui, server, debug=True)
