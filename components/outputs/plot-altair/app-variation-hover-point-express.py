import altair as alt
import pandas as pd
from shiny.express import render, ui
from shinywidgets import reactive_read, render_altair  # <<
from vega_datasets import data

df = data.cars()

"Hover over a point to see its info"

with ui.layout_column_wrap():

    @render_altair
    def jchart():
        hover = alt.selection_point(  # <<
            name="hover",  # <<
            on="mouseover",  # <<
            empty=False,  # <<
        )  # <<
        return (
            alt.Chart(df)
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
        # pt is a JupyterChart IndexSelection object
        pt = reactive_read(jchart.widget.selections, "hover")  # <<
        hover_idx = pt.value
        selected = df.iloc[hover_idx]
        if hover_idx:
            transposed = selected.T.reset_index()
            transposed.columns = ["Variable", "Value"]
            return transposed
        else:
            return pd.DataFrame({"Variable": df.columns, "Value": ""})
