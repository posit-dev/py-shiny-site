from shiny.express import render, ui
import matplotlib.pyplot as plt

with ui.card(full_screen=True, height="350px"):  # <<
    ui.card_header(  # <<
        "Sales Trend",  # <<
        class_="bg-dark",  # <<
    )  # <<

    @render.plot  # <<
    def plot():  # <<
        # Generate sample sales data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        sales = [45, 52, 48, 61, 58, 67, 71, 69, 74, 78, 82, 88]

        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.plot(months, sales, marker='o', linewidth=2, markersize=5, color='steelblue')
        ax.fill_between(range(len(months)), sales, alpha=0.3, color='steelblue')
        ax.set_title("Monthly Sales Trend", fontsize=10, pad=8)
        ax.set_xlabel("Month", fontsize=8)
        ax.set_ylabel("Sales ($K)", fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=7)
        plt.xticks(rotation=45)
        plt.tight_layout(pad=2.0)
        return fig  # <<
