import altair as alt
import pandas as pd
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_altair

source = pd.DataFrame({
    "a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
    "b": [28, 55, 43, 91, 81, 53, 19, 87, 52],
})

app_ui = ui.page_fixed(
    output_widget("chart"),
    ui.input_radio_buttons(
        "chart_color", "Color", ["blue", "crimson"], inline=True
    ),
)


def server(input, output, session):
    @render_altair
    def chart():
        return alt.Chart(source).mark_bar().encode(x="a", y="b")

    @reactive.effect
    @reactive.event(input.chart_color)
    def update():
        jchart = chart.widget
        jchart.chart = jchart.chart.mark_bar(
            color=input.chart_color(),
            cornerRadius=10,
        )


app = App(app_ui, server)
