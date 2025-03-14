from shiny.express import input, render, ui

ui.input_text("Text", "Enter Text", "")
ui.output_code("text", placeholder=True)  # <<

with ui.hold():  # <<

    @render.code  # <<
    def text():
        return input.Text()
