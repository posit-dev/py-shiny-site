## file: app.py
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_select( #<<
        "select", #<<
        "Select an option below:", #<<
        {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"}, #<<
    ), #<<
    ui.output_text("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return f"{input.select()}"

app = App(app_ui, server)
