from shiny import App, render, ui
app_ui = ui.page_fluid(
    ui.input_checkbox("x", "Checkbox Checkbox").add_class("mb-0"),
    ui.output_text_verbatim("txt"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"}
)
def server(input, output, session):
    @output
    @render.text
    def txt():
        return f""
app = App(app_ui, server)
