from shiny import App, reactive, ui

code_samples = {
    "python": "def greet(name):\n    return f'Hello, {name}!'",
    "javascript": "function greet(name) {\n  return `Hello, ${name}!`;\n}",
    "sql": "SELECT greeting FROM greetings\nWHERE name = 'World';",
}

app_ui = ui.page_fluid(
    ui.input_select(
        "language",
        "Language:",
        choices=list(code_samples.keys()),
        selected="python",
    ),
    ui.input_switch("read_only", "Read only", value=False),
    ui.input_code_editor(
        "code",
        "Code editor:",
        code_samples["python"],
        language="python",
    ),
    {"class": "p-3 mx-auto"},
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.language)
    def _():
        ui.update_code_editor(
            "code",
            value=code_samples[input.language()],
            language=input.language(),
        )

    @reactive.effect
    @reactive.event(input.read_only)
    def _():
        ui.update_code_editor("code", read_only=input.read_only())


app = App(app_ui, server)
