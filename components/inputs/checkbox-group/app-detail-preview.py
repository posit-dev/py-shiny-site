## file: app.py
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_checkbox_group(
        "checkbox_group",
        "Checkbox group",
        {
            "a": "A",
            "b": "B",
            "c": "C",
        },
    ),
    ui.output_text("value"),
    {"class": "vh-100 d-flex align-items-center px-4"},
)


def server(input, output, session):
    @output
    @render.text
    def value():
        return ", ".join(input.checkbox_group())


app = App(app_ui, server)
