from shiny import App, ui

app_ui = ui.page_fluid(
    ui.input_switch("switch", "Make it switchable", True).add_class("mb-0"),
    ui.output_ui("value"),
    {
        "class": "vh-100 d-flex flex-column justify-content-center align-items-center px-4"
    },
)


def server(input, output, session):
    pass


app = App(app_ui, server)
