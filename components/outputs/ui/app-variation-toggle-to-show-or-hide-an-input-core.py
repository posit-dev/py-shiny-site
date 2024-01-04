from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_switch("show_slider", "Show slider"),
    ui.output_ui("uiElement"), #<<
)

def server(input, output, session):
    @render.ui #<<
    def uiElement(): #<<
        if (input.show_slider()): #<<
            return ui.input_slider("slider", "Choose a number", min=1, max=10, value=5) #<<

app = App(app_ui, server)
