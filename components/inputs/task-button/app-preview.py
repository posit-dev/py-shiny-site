from shiny import ui, App

app_ui = ui.page_fluid(
    ui.input_task_button("process", "Process Data"),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
