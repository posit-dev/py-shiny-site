# FIXME: Rewrite as an Express app
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("number", "Enter a number:", 1, min=1, max=10),
    ui.output_ui("uiElement"), #<<
)

def server(input, output, session):
    @render.ui #<<
    def uiElement(): #<<
        return ui.input_slider("slider", "Current number:", min=1, max=10, value=input.number()), #<<

app = App(app_ui, server)
