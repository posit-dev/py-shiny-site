from shiny import ui, App

app_ui = ui.page_fluid(
    ui.h4("Different Programming Languages"),
    ui.input_code_editor(
        "python_code",
        "Python",
        "def hello():\n    print('Hello, Python!')",
        language="python",
        height="120px",
    ),
    ui.input_code_editor(
        "javascript_code",
        "JavaScript",
        "function hello() {\n  console.log('Hello, JavaScript!');\n}",
        language="javascript",
        height="120px",
    ),
    ui.input_code_editor(
        "sql_code",
        "SQL",
        "SELECT * FROM users\nWHERE active = true;",
        language="sql",
        height="100px",
    ),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
