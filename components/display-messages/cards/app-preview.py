from shiny import App, render, ui
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Diamond Cut Distribution", class_="bg-primary text-white"),
        ui.output_plot("plot"),
        full_screen=True,
        height="450px",
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    @render.plot
    def plot():
        # Create sample diamond data
        cuts = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
        counts = [1610, 4906, 12082, 13791, 21551]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(cuts, counts, color=['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#2ecc71'])
        ax.set_xlabel('Cut Quality', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title('Distribution of Diamond Cuts', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        return fig


app = App(app_ui, server)
