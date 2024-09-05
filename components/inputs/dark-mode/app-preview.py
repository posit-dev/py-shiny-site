from shiny import ui, render, App

app_ui = ui.page_fluid(
  ui.input_dark_mode().add_class("mb-0"),
  {
    "class": "vh-100 d-flex flex-column justify-content-center align-items-center px-4"
  },
)

def server(input, output, session):
    pass

app = App(app_ui, server)
