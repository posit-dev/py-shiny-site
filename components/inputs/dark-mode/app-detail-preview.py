## file: app.py
from shiny import ui, render, App

app_ui = ui.page_fluid(ui.input_dark_mode()).add_class("p-5")

def server(input, output, session):
    pass

app = App(app_ui, server)
