## file: app.py
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_switch("switch", "Switch", True),
    ui.output_ui("value"),
).add_class("p-5")

def server(input, output, session):
    @output
    @render.ui
    def value():
        return input.switch()

app = App(app_ui, server)
