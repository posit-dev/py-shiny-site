# FIXME: Rewrite as an Express app
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_slider("slider", "Slider", min=0, max=100, value=[35, 65]), #<<
    ui.output_text_verbatim("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return f"{input.slider()}"

app = App(app_ui, server)
