from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_switch("show_slider", "Show slider", True),
    ui.output_ui("uiElement"),
    {"class": "vh-100 d-flex flex-column pt-4 px-4"},
)


def server(input, output, session):
    @render.ui
    def uiElement():
        if input.show_slider():
            return ui.input_slider("slider", "", min=1, max=10, value=5)


app = App(app_ui, server)
