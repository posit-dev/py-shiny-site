import altair as alt
import pandas as pd
from shiny.express import render
from shinywidgets import reactive_read, render_altair
from vega_datasets import data

df = data.cars()

"Click a legend to filter"


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
        " and ".join([f"`{col}` == {repr(val)}" for col, val in sel.items()])
        for sel in selected
    ])

    return df.query(filter) if filter else pd.DataFrame(columns=df.columns)
