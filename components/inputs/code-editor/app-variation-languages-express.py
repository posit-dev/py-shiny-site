from shiny.express import ui

ui.input_code_editor(
    "python_code",
    "Python",
    "def hello():\n    print('Hello, Python!')",
    language="python",  # <<
)

ui.input_code_editor(
    "javascript_code",
    "JavaScript",
    "function hello() {\n  console.log('Hello, JavaScript!');\n}",
    language="javascript",  # <<
)

ui.input_code_editor(
    "sql_code",
    "SQL",
    "SELECT * FROM users\nWHERE active = true;",
    language="sql",  # <<
)
