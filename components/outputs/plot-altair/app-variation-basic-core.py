import altair as alt
import pandas as pd
from shiny import App, render, ui
from shinywidgets import output_widget, render_altair

source = pd.DataFrame({
    "a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
    "b": [28, 55, 43, 91, 81, 53, 19, 87, 52],
})

app_ui = ui.page_fluid(
    output_widget("chart"),
    ui.output_text("chart_type"),
    ui.output_text("chart_widget_type"),
)


def server(input, output, session):
    @render_altair
    def chart():
        return alt.Chart(source).mark_bar().encode(x="a", y="b")

    @render.text
    def chart_type():
        return f"Type of chart: {type(chart)}"

    @render.text
    def chart_widget_type():
        return f"Type of chart.widget: {type(chart.widget)}"


app = App(app_ui, server)
