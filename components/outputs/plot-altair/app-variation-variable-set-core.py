import altair as alt
import numpy as np
import pandas as pd
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, reactive_read, render_altair

rand = np.random.RandomState(42)

df = pd.DataFrame({"xval": range(100), "yval": rand.randn(100).cumsum()})
initial = 50

app_ui = ui.page_fixed(
    ui.output_text("cutoff"),
    ui.div(
        output_widget("plot"),
        style="margin-bottom: 40px;",
    ),
    ui.input_radio_buttons(
        "cut_preset",
        "Cutoff Presets",
        [25, 50, 75],
        inline=True,
        selected=initial,
    ),
)


def server(input, output, session):
    @render.text
    def cutoff():
        jchart = plot.widget
        cut = reactive_read(jchart.params, names="cutoff")
        return f"Current cutoff: {int(cut)}"

    @render_altair
    def plot():
        slider = alt.binding_range(min=0, max=100, step=1)
        cutoff = alt.param(name="cutoff", bind=slider, value=initial)
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

    @reactive.effect
    @reactive.event(input.cut_preset)
    def update():
        jchart = plot.widget
        jchart.params.cutoff = int(input.cut_preset())


app = App(app_ui, server)
