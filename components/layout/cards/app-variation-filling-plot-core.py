from shiny import App, render, ui
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Sales Trend"),
        ui.output_plot("plot"),
        height="400px",
        full_screen=True
    )
)


def server(input, output, session):
    @render.plot
    def plot():
        # Generate sample data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        sales = [45, 52, 48, 61, 58, 67]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(months, sales, marker='o', linewidth=2, markersize=8, color='steelblue')
        ax.set_title("Monthly Sales Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Sales ($K)")
        ax.grid(True, alpha=0.3)
        return fig


app = App(app_ui, server)
