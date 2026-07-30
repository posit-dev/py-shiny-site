from shiny.express import input, render, ui

ui.input_submit_textarea(
    "quick_message",
    "Quick message:",
    submit_key="enter",  # <<
    placeholder="Press Enter to submit, Shift+Enter for a new line",
)


@render.code
def value():
    if "quick_message" in input:
        return f"You submitted: {input.quick_message()}"
    return "Nothing submitted yet."
