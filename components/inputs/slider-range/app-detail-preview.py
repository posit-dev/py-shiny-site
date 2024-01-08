## file: app.py
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_slider("slider", "", min=0, max=100, value=[35, 65]).add_class("pt-5 mx-auto text-center"),
    ui.output_text_verbatim("value"),
    {"class": "vh-100 justify-content-center align-items-center px-5"}
).add_class("my-auto text-center")

def server(input, output, session):
    @output
    @render.text
    def value():
        return f"{input.slider()}"

app = App(app_ui, server)
