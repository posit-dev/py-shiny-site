## file: app.py
from shiny import App, render, ui
app_ui = ui.page_fluid(
    ui.row(
        ui.column(6, ui.input_checkbox("checkbox", "Checkbox", True).add_class("mb-0 text-center")), 
        ui.column(6, ui.output_ui("value").add_class("mb-0 text-center")),
        {"class": "vh-100 justify-content-center align-items-center px-5"}
    )
)

def server(input, output, session):
    @render.ui
    def value():
        return input.checkbox()
app = App(app_ui, server)
