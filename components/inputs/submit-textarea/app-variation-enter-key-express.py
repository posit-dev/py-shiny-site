from shiny.express import input, render, ui

ui.p("Press Enter (without Ctrl/Cmd) to submit:")

ui.input_submit_textarea(
    "quick_message",
    "Quick message:",
    submit_key="enter",
    placeholder="Press Enter to submit, Shift+Enter for new line",
)

@render.text
def output():
    if "quick_message" in input:
        return f"Submitted: {input.quick_message()}"
    return "No message yet"
