from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_selectize( #<<
        "selectize", #<<
        "Select options below:", #<<
        {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"}, #<<
        multiple=True #<<
    ), #<<
    ui.output_text("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return f"{input.selectize()}"

app = App(app_ui, server)
