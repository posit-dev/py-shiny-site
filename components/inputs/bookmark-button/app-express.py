from shiny.express import app_opts, input, render, ui

app_opts(bookmark_store="url") # <<

ui.input_text("name", "Your name:", "")
ui.input_bookmark_button() # <<

@render.text
def greeting():
    return f"Hello, {input.name() or 'stranger'}!"
