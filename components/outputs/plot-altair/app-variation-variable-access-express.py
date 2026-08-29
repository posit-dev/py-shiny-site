import altair as alt
import numpy as np
import pandas as pd
from shiny.express import render
from shinywidgets import reactive_read, render_altair

rand = np.random.RandomState(42)

df = pd.DataFrame({"xval": range(100), "yval": rand.randn(100).cumsum()})


@render.text
def cutoff():
    jchart = plot.widget
    cut = reactive_read(jchart.params, names="cutoff")
    return f"Current cutoff: {cut}"


@render_altair
def plot():
    slider = alt.binding_range(min=0, max=100, step=1)
    cutoff = alt.param(name="cutoff", bind=slider, value=50)
    predicate = alt.datum.xval < cutoff

    chart = (
        alt.Chart(df)
        .mark_point()
        .encode(
            x="xval",
            y="yval",
            color=alt.when(predicate)
            .then(alt.value("red"))
            .otherwise(alt.value("blue")),
        )
        .add_params(cutoff)
    )
    return chart
