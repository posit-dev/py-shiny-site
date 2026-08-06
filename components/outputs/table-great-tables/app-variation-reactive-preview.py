## file: app.py
import pandas as pd
from great_tables import GT
from great_tables.shiny import output_gt, render_gt
from shiny import App, ui

sales = pd.DataFrame(
    {
        "product": ["Essentials", "Plus", "Pro", "Teams", "Enterprise"],
        "revenue": [184000, 267000, 352000, 296000, 421000],
        "margin": [0.18, 0.23, 0.29, 0.25, 0.33],
    }
)

app_ui = ui.page_fluid(
    ui.input_slider("min_revenue", "Minimum revenue", 0, 500000, 0, step=50000),
    output_gt("sales_table"),
    title="Great Tables",
)


def server(input, output, session):
    @render_gt
    def sales_table():
        subset = sales[sales["revenue"] >= input.min_revenue()]
        return (
            GT(subset, rowname_col="product")
            .tab_header(title="Quarterly product performance")
            .fmt_currency(columns="revenue", decimals=0)
            .fmt_percent(columns="margin", decimals=1)
        )


app = App(app_ui, server)

## file: requirements.txt
# Pinned below 0.22: 0.22.0 added a hard multimark dependency, which has no
# pure Python wheel and so cannot install under Pyodide.
great-tables<0.22
