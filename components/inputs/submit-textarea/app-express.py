from shiny.express import input, render, ui

ui.input_submit_textarea("message", "Enter your message:")  # <<


@render.code
def value():
    if "message" in input:
        return f"You submitted: {input.message()}"
    return "Nothing submitted yet."
