## file: app.py
from shiny import ui, render, App

app_ui = ui.page_fluid(ui.input_dark_mode()).add_class("h-100 w-100 align-content-center text-center")

def server(input, output, session):
    pass

app = App(app_ui, server)
