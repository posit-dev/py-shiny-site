from shiny import render
from shiny.express import input, ui


ui.input_date_range("daterange", "Date range", start="2020-01-01")  # <<


@render.text
def value():
    return f"{input.daterange()[0]} to {input.daterange()[1]}"
