import pandas as pd
from great_tables import GT, loc, md, style
from great_tables.shiny import output_gt, render_gt
from shiny import App, ui


sales = pd.DataFrame(
    {
        "product": ["Essentials", "Plus", "Pro", "Teams", "Enterprise"],
        "revenue": [184000, 267000, 352000, 296000, 421000],
        "profit": [33000, 61000, 102000, 74000, 139000],
        "margin": [0.18, 0.23, 0.29, 0.25, 0.33],
        "growth": [0.08, 0.14, 0.21, -0.03, 0.27],
    }
)


app_ui = ui.page_fluid(output_gt("sales_table"), title="Great Tables")


def server(input, output, session):
    @render_gt
    def sales_table():
        return (
            GT(sales, rowname_col="product")
            .tab_header(
                title="Quarterly product performance",
                subtitle="Revenue, profitability, and year-over-year growth",
            )
            .tab_stubhead(label="Product")
            .tab_spanner(label="Financials", columns=["revenue", "profit", "margin"])
            .cols_label(
                revenue="Revenue", profit="Profit", margin="Margin", growth="YoY growth"
            )
            .fmt_currency(columns=["revenue", "profit"], decimals=0)
            .fmt_percent(columns=["margin", "growth"], decimals=1)
            .data_color(
                columns="margin",
                palette=["#f8d7da", "#fff3cd", "#d1e7dd"],
                domain=[0.15, 0.35],
            )
            .tab_style(
                style=[style.fill("#e7f5ff"), style.text(weight="bold")],
                locations=loc.body(rows=[4]),
            )
            .opt_row_striping()
            .tab_source_note(md("**Source:** Illustrative quarterly results"))
        )


app = App(app_ui, server)
