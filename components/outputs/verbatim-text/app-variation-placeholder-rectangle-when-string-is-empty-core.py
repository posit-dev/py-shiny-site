from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_text("Text", "Enter Text", ""),
    ui.output_text_verbatim("text", placeholder = True) #<<
)

def server(input, output, session):
    @render.text #<<
    def text():
        return input.Text()

app = App(app_ui, server)
