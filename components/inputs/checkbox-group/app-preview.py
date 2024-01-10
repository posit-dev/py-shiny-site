from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_checkbox_group(
        "checkbox_group",
        "",
        {
            "a": "Watch me Whip",
            "b": "Watch me Nae Nae",
            "c": "Watch neither",
        },
    ).add_class("mb-0"),
    ui.output_text("value"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    @output
    @render.text
    def value():
        return ""


app = App(app_ui, server)
