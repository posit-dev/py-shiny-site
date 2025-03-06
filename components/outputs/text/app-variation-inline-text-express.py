from shiny.express import input, render, ui

ui.input_text("Text", "Enter text", "Hello Shiny")
"You entered:"


@render.text(inline=True)  # <<
def text():
    return input.Text()
