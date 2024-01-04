# FIXME: Rewrite as an Express app
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_checkbox("checkbox", "Checkbox", False), #<<
    ui.output_ui("value"),
)

def server(input, output, session):
    @render.ui
    def value():
        return input.checkbox()

app = App(app_ui, server)
