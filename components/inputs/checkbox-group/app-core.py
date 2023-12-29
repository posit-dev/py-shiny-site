from shiny import App, render, req, ui

app_ui = ui.page_fluid(
    ui.input_checkbox_group( #<<
        "checkbox_group", #<<
        "Checkbox group", #<<
        { #<<
            "a": "A", #<<
            "b": "B", #<<
            "c": "C", #<<
        }, #<<
    ), #<<
    ui.output_text("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return ", ".join(input.checkbox_group())

app = App(app_ui, server)
