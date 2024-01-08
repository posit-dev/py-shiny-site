## file: app.py
from shiny import App, render, ui
app_ui = ui.page_fluid(
    ui.input_radio_buttons( 
        "radio", 
        "Radio buttons", 
        {"1": "Option 1", "2": "Option 2", "3": "Option 3"}, 
    ), 
    ui.output_ui("value"),
    {"class": "vh-100 d-flex align-items-center px-4"}
)
def server(input, output, session):
    @render.ui
    def value():
        return input.radio()
app = App(app_ui, server)



