# FIXME: Rewrite as an Express app
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("numeric", "Numeric input", 1, min=1, max=10), #<<
    ui.output_text_verbatim("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return input.numeric()

app = App(app_ui, server)
