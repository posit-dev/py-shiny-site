from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("add_button", "Add a UI element"),
    ui.output_ui("uiElement"), #<<
)

def server(input, output, session):
    @render.ui #<<
    @reactive.event(input.add_button) #<<
    def uiElement(): #<<
        return ui.input_slider("slider", "Choose a number", min=1, max=10, value=5), #<<

app = App(app_ui, server)
