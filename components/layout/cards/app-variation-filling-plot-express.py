from shiny.express import ui, render
import matplotlib.pyplot as plt

with ui.card(height="400px", full_screen=True):
    ui.card_header("Sales Trend")

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
