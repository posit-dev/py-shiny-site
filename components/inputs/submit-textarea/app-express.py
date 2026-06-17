from shiny.express import input, render, ui

ui.input_submit_textarea("message", "Enter your message:") # <<

@render.text
def message_output():
    if "message" in input:
        return f"You submitted: {input.message()}"
    return "No message submitted yet"
