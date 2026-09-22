from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_text("text", "Text input", "Enter text..."),  # <<
    ui.output_code("value"),
)


def server(input, output, session):
    @render.code
    def value():
        return input.text()


app = App(app_ui, server)
