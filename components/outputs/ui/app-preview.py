from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_switch("show_ui", "Show UI", True),
    ui.output_ui("contents"),
    {"class": "vh-100 d-flex flex-column pt-4 px-4"},
)


def server(input, output, session):
    @render.ui
    def contents():
        if input.show_ui():
            return ui.TagList(
                ui.input_slider("slider", "", min=1, max=10, value=5),
                ui.output_code("value"),
            )

    @render.code
    def value():
        return f"slider: {input.slider()}"


app = App(app_ui, server)
