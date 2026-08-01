from shiny import App, ui

app_ui = ui.page_fluid(
    ui.input_code_editor(
        "python_code",
        "Python",
        "def hello():\n    print('Hello, Python!')",
        language="python",  # <<
    ),
    ui.input_code_editor(
        "javascript_code",
        "JavaScript",
        "function hello() {\n  console.log('Hello, JavaScript!');\n}",
        language="javascript",  # <<
    ),
    ui.input_code_editor(
        "sql_code",
        "SQL",
        "SELECT * FROM users\nWHERE active = true;",
        language="sql",  # <<
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
