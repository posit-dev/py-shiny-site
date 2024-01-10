from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_radio_buttons(
        "radio",
        "Never gonna:",
        {"1": "Give you up", "2": "Let you down"},
    ).add_class("mb-0"),
    ui.output_ui("value"),
    {
        "class": "vh-100 d-flex flex-column justify-content-center align-items-center px-4"
    },
)


def server(input, output, session):
    @output
    @render.text
    def txt():
        return ""


app = App(app_ui, server, debug=True)
