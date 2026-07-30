from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_submit_textarea(
        "quick_message",
        "Quick message:",
        submit_key="enter",  # <<
        placeholder="Press Enter to submit, Shift+Enter for a new line",
    ),
    ui.output_code("value"),
)


def server(input, output, session):
    @render.code
    def value():
        if "quick_message" in input:
            return f"You submitted: {input.quick_message()}"
        return "Nothing submitted yet."


app = App(app_ui, server)
