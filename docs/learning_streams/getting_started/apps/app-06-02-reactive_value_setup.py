from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from shiny import render
from shiny.express import input, ui
from shinywidgets import render_widget
import yfinance as yf

ui.page_opts(title="Census Visualization", fillable=True)

with ui.sidebar(bg="#f8f8f8"):
    ui.help_text("Select a stock to get from yahoo finance. Max 90 day history.")
    ui.input_select(
        "stock",
        "Symbol",
        [
            "IBM",
            "GOOG",
            "T",
            "LULU",
        ],
        selected="GOOG",
    )

    ui.input_slider("days", "Days from today:", min=0, max=90, value=30)

    ui.input_radio_buttons(
      "column",
      "Stock Data To Plot",
      ["Open", "High", "Low", "Close", "Volume", "Dividends"],
    )

@render_widget
def plot():
    # calculate date range
    end_date = datetime.today()
    start_date = end_date - timedelta(days=input.days())

    # get the stock data for symbol and date range
    stock = yf.Ticker(input.stock())
    data = stock.history(start=start_date, end=end_date)
    data['date'] = pd.to_datetime(data.index)

    fig = px.line(
      data,
      x='date',
      y=input.column(),
    )

    return fig
