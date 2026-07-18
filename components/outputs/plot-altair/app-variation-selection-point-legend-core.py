import altair as alt
import pandas as pd
from shiny import App, render, ui
from shinywidgets import output_widget, reactive_read, render_altair
from vega_datasets import data

df = data.cars()

app_ui = ui.page_fluid(
    ui.markdown("Click a legend to filter"),
    output_widget("chart"),
    ui.output_data_frame("hover_info"),
)


def server(input, output, session):
    @render_altair
    def chart():
        brush = alt.selection_point(
            name="point", encodings=["color"], bind="legend"
        )

        return (
            alt.Chart(df)
            .mark_point()
            .encode(
                x="Horsepower:Q",
                y="Miles_per_Gallon:Q",
                color=alt.when(brush)
                .then("Origin:N")
                .otherwise(alt.value("grey")),
            )
            .add_params(brush)
        )

    @render.data_frame
    def hover_info():
        jchart = chart.widget
        # pt is an PointSelection object
        pt = reactive_read(jchart.selections, names="point")
        selected = pt.value

        filter = " or ".join([
            " and ".join([
                f"`{col}` == {repr(val)}" for col, val in sel.items()
            ])
            for sel in selected
        ])

        return df.query(filter) if filter else pd.DataFrame(columns=df.columns)


app = App(app_ui, server)
