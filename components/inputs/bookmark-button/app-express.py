from shiny.express import input, render, ui

ui.input_text("name", "Your name:", "")
ui.input_bookmark_button() # <<

@render.text
def greeting():
    return f"Hello, {input.name() or 'stranger'}!"
