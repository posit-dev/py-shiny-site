from shiny import ui, App

app_ui = ui.page_fluid(
    ui.h4("Read-only Code Display"),
    ui.input_code_editor(
        "readonly_code",
        "Example Code (Read-only)",
        "# This code cannot be edited\ndef calculate_sum(a, b):\n    return a + b\n\nresult = calculate_sum(10, 20)\nprint(f'Result: {result}')",
        language="python",
        height="180px",
        read_only=True,
    ),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
