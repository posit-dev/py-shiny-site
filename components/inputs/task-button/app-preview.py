from shiny import ui, App

app_ui = ui.page_fluid(
    ui.input_task_button("process", "Process Data"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)

def server(input, output, session):
    pass

app = App(app_ui, server)
