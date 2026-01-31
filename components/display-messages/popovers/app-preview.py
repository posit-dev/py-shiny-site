from shiny import ui, App

app_ui = ui.page_fluid(
    ui.popover(
        ui.input_action_button("btn", "Show popover"),
        "Popover content appears here",
        title="Info",
    ),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
