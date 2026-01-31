## file: app.py
from shiny import App, render, ui
import plotly.express as px

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Diamond Cut Distribution",
            class_="bg-dark",
        ),
        ui.output_plot("plot"),
        full_screen=True,
        height="450px",
    )
)


def server(input, output, session):
    @render.plot
    def plot():
        import matplotlib.pyplot as plt

        df = px.data.diamonds()
        cut_counts = df["cut"].value_counts()

        fig, ax = plt.subplots(figsize=(8, 6))
        cut_counts.plot(kind="bar", ax=ax, color="steelblue")
        ax.set_title("Diamond Cut Distribution")
        ax.set_xlabel("Cut")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45)
        return fig


app = App(app_ui, server)
