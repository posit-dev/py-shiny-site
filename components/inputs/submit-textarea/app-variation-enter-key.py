from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.p("Press Enter (without Ctrl/Cmd) to submit:"),
    ui.input_submit_textarea(
        "quick_message",
        "Quick message:",
        submit_key="enter",
        placeholder="Press Enter to submit, Shift+Enter for new line",
    ),
    ui.output_text_verbatim("output"),
)

def server(input, output, session):
    @render.text
    def output():
        if "quick_message" in input:
            return f"Submitted: {input.quick_message()}"
        return "No message yet"

app = App(app_ui, server)
