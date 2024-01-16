## file: app.py
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("numeric", "", 1, min=1, max=10).add_class(
        "pt-5 mx-auto text-center"
    ),
    ui.output_text_verbatim("value"),
    {"class": "vh-100 justify-content-center align-items-center px-5"},
).add_class("my-auto text-center")


def server(input, output, session):
    @render.text
    def value():
        return input.numeric()


app = App(app_ui, server)
