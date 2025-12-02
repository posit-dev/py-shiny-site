import altair as alt
from shiny.express import render
from shinywidgets import reactive_read, render_altair, render_widget  # <<
from vega_datasets import data

source = data.cars()

"Hover over a point to see its info"


@render_widget
def jchart():
    hover = alt.selection_point(
        name="hover", on="mouseover", empty=False
    )  # <<
    return (
        alt.Chart(source)
        .mark_circle(size=60)
        .encode(
            x="Horsepower:Q",
            y="Miles_per_Gallon:Q",
            color="Origin:N",
            opacity=alt.condition(hover, alt.value(1), alt.value(0.1)),
            size=alt.condition(hover, alt.value(250), alt.value(50)),
        )
        .add_params(hover)
    )


@render.data_frame
def hover_info():
    pt = reactive_read(jchart.widget.selections, "hover")  # <<
    indices = pt.value
    return source.iloc[indices]
