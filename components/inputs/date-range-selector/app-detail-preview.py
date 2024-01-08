## file: app.py
from datetime import date

from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_date_range("daterange", "", start="2020-01-01").add_class("pt-5 mx-auto text-center"),
    ui.output_text("value"),
        {"class": "vh-100 justify-content-center align-items-center px-5"}
).add_class("my-auto text-center")


def server(input, output, session):
    @output
    @render.text
    def value():
        return f"{input.daterange()[0]} to {input.daterange()[1]}"


app = App(app_ui, server)
