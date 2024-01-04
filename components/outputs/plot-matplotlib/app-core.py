import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of bins", 0, 100, 20),
    ui.output_plot("plot"),  #<<
)

def server(input, output, session):
    @render.plot(alt="A histogram")  #<<
    def plot():  #<<
        df = load_penguins()
        mass = df["body_mass_g"]

        fig, ax = plt.subplots()
        ax.hist(mass, input.n(), density=True)
        ax.set_title("Palmer Penguin Masses")
        ax.set_xlabel("Mass (g)")
        ax.set_ylabel("Density")

        return fig  #<<

app = App(app_ui, server, debug=True)
