# FIXME: Rewrite as an Express app
# see shiny-live page for details on additional files

from pathlib import Path

import pandas as pd
import plotly.express as px
import shinywidgets as sw
from shiny import App, ui

appdir = Path(__file__).parent

app_ui = ui.page_fillable(
    ui.include_css(appdir / "styles.css"),
    ui.value_box(
        "Total Sales in Q2",
        "$2.45M",
        {"class": "shadow-none"},
        showcase=sw.output_widget("sparkline"),
        showcase_layout=ui.showcase_left_center(width="40%"),
    ),
    padding=0,
    fillable_mobile=True,
)

def server(input, output, session):
    @sw.render_widget
    def sparkline():
        economics = pd.read_csv(appdir / "economics.csv")
        fig = px.line(economics, x="date", y="psavert")
        fig.update_traces(
            line_color="#406EF1",
            line_width=1,
            fill="tozeroy",
            fillcolor="rgba(64,110,241,0.2)",
            hoverinfo="y",
        )
        fig.update_xaxes(visible=False, showgrid=False)
        fig.update_yaxes(visible=False, showgrid=False)
        fig.update_layout(
            height=60,
            hovermode="x",
            margin=dict(t=0, r=0, l=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        return fig

app = App(app_ui, server)
