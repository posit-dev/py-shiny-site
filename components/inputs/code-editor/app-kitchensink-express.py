from shiny.express import input, render, ui

ui.tags.head(ui.tags.title("Code Editor Demo"))

# Create a code editor with all possible parameters
ui.input_code_editor(
    id="editor",
    label="Edit the code, then press Ctrl/Cmd + Enter:",
    value='def greet(name):\n    return f"Hello, {name}!"\n\n\nprint(greet("Shiny"))',
    language="python",
    height="260px",
    width="100%",
    theme_light="github-light",
    theme_dark="github-dark",
    read_only=False,
    line_numbers=True,
    word_wrap=True,
    tab_size=4,
    indentation="space",
    fill=False,
)

ui.br()
ui.h4("Submitted code:")


@render.code
def submitted():
    return input.editor()
