# Open in shinylive to see additional files

from pathlib import Path

import pandas as pd
import plotly.express as px
import shinywidgets as sw
from shiny.express import ui

appdir = Path(__file__).parent

ui.include_css(appdir / "styles.css")

with ui.value_box(showcase=sw.output_widget("sparkline"), showcase_layout="bottom"):
    "Total Sales in Q2"
    "$2.45M"

    with ui.hold():

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
                height=100,
                hovermode="x",
                margin=dict(t=0, r=0, l=0, b=0),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            return fig
