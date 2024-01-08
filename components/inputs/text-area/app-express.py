# FIXME: Rewrite as an Express app
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_text_area("textarea", "Text input", "Hello World"), #<<
    ui.output_text_verbatim("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return input.textarea()

app = App(app_ui, server)
