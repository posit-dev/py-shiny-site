from shiny import ui, App

app_ui = ui.page_fluid(
    ui.popover( # <<
        ui.input_action_button("btn", "Click me"),
        "This is a popover with helpful information!",
        title="Popover Title",
    ),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
