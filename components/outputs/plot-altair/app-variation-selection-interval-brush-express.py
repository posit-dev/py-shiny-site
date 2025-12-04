import altair as alt
import pandas as pd
from shiny.express import render, ui
from shinywidgets import reactive_read, render_altair
from vega_datasets import data

df = data.cars()

"Click and drag a box over points to see its data"


@render_altair
def chart():
    brush = alt.selection_interval(name="brush")
    return (
        alt.Chart(df)
        .mark_circle(size=60)
        .encode(
            x="Horsepower:Q",
            y="Miles_per_Gallon:Q",
            color="Origin:N",
        )
        .add_params(brush)
    )


@render.data_frame
def hover_info():
    jchart = chart.widget
    # brushed is an IntervalSelection object
    brushed = reactive_read(jchart.selections, names="brush")

    brush_idx = brushed.value.items()
    filter = " and ".join([f"{v[0]} <= `{k}` <= {v[1]}" for k, v in brush_idx])

    return df.query(filter) if filter else pd.DataFrame(columns=df.columns)
