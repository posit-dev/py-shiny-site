from shiny import ui, App

app_ui = ui.page_fluid(
    ui.input_code_editor(
        "code",
        "Code Editor",
        "# Python code editor\nprint('Hello!')",
        language="python",
        height="150px",
    ),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
