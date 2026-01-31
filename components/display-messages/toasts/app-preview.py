from shiny import ui, App

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show Toast"),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
