from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_code_editor(
        "code",
        "Enter Python code:",
        "def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))",
        language="python",
    ),
    ui.output_code("value"),
    {"class": "p-3 mx-auto"},
)


def server(input, output, session):
    @render.code
    def value():
        return input.code()


app = App(app_ui, server)
