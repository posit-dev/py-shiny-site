from starlette.requests import Request
from shiny import ui, render, App

def app_ui(request: Request): # <<
    return ui.page_fluid(
        ui.input_text("name", "Your name:", ""),
        ui.input_bookmark_button(), # <<
        ui.output_text_verbatim("greeting"),
    )

def server(input, output, session):
    @render.text
    def greeting():
        return f"Hello, {input.name() or 'stranger'}!"

app = App(app_ui, server, bookmark_store="url") # <<
