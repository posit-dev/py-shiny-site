from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_slider("slider", "Slider", 0, 100, 50),  # <<
    ui.output_text_verbatim("value"),
)


def server(input, output, session):
    @render.text
    def value():
        return f"{input.slider()}"


app = App(app_ui, server)
