import pandas as pd
from great_tables import GT
from great_tables.shiny import render_gt
from shiny.express import ui

sales = pd.DataFrame(
    {
        "product": ["Essentials", "Plus", "Pro", "Teams", "Enterprise"],
        "revenue": [184000, 267000, 352000, 296000, 421000],
        "margin": [0.18, 0.23, 0.29, 0.25, 0.33],
    }
)

ui.page_opts(title="Great Tables", fillable=True)


@render_gt  # <<
def sales_table():
    return (
        GT(sales, rowname_col="product")
        .tab_header(title="Quarterly product performance")
        .fmt_currency(columns="revenue", decimals=0)
        .fmt_percent(columns="margin", decimals=1)
    )
