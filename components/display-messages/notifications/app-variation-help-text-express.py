# FIXME: Rewrite as an Express app
from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show help text"),
)

def server(input, output, session):
    # ui.help_text() is only a ui component
    pass

app = App(app_ui, server)
