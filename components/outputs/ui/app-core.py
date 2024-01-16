from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_switch("show_slider", "Show slider", True),
    ui.output_ui("ui_slider"),  # <<
)


def server(input, output, session):
    @render.ui  # <<
    @reactive.event(input.show_slider)  # <<
    def ui_slider():  # <<
        if input.show_slider():
            value = input.slider() if "slider" in input else 5
            return ui.input_slider(
                "slider", "Choose a number", min=1, max=10, value=value
            )


app = App(app_ui, server)
