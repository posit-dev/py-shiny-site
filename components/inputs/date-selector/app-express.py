# FIXME: Rewrite as an Express app
from datetime import date

from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_date("date", "Date"), #<<
    ui.output_text("value")
)

def server(input, output, session):
    @render.text
    def value():
        return input.date()

app = App(app_ui, server)
