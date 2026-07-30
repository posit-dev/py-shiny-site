from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.title("Code Editor Demo")),
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
    ),
    # Add some spacing
    ui.br(),
    # Add a header for the output
    ui.h4("Submitted code:"),
    # Add the output
    ui.output_code("submitted"),
)


# Define the server
def server(input, output, session):
    @render.code
    def submitted():
        return input.editor()


# Create the app
app = App(app_ui, server)
