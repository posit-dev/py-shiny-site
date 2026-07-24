from shiny.express import input, render, ui

ui.input_text("Text", "Enter Text", "")
ui.output_text_verbatim("text", placeholder=True)  # <<

with ui.hold():  # <<

    @render.text  # <<
    def text():
        return input.Text()
