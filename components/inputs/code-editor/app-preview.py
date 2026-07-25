from shiny import App, ui

app_ui = ui.page_fluid(
    ui.input_code_editor(
        "code",
        "",
        "def greet(name):\n    return f'Hello, {name}!'",
        language="python",
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
