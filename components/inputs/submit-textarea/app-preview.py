from shiny import ui, App

app_ui = ui.page_fluid(
    ui.input_submit_textarea(
        "message",
        "Your message:",
        placeholder="Type here and press Ctrl+Enter...",
    ),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
