from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_file("f", "Pick a file, any file"),
    "Input file data:",
    ui.output_text_verbatim("txt"),
)


def server(input, output, session):
    @render.text
    def txt():
        return input.f()


app = App(app_ui, server, debug=True)
