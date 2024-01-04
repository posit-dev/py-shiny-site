# FIXME: Rewrite as an Express app
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_switch("switch", "Switch", False), #<<
    ui.output_ui("value"),
)

def server(input, output, session):
    @render.ui
    def value():
        return input.switch()

app = App(app_ui, server)
