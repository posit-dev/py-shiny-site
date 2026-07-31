from shiny import App, ui

app_ui = ui.page_fluid(
    ui.input_checkbox("show", "Show advanced options", False),
    ui.panel_conditional(  # <<
        "input.show",  # <<
        ui.input_radio_buttons("kind", "Control kind", ["slider", "select"]),
    ),  # <<
    ui.panel_conditional(  # <<
        "input.show && input.kind === 'slider'",  # <<
        ui.input_slider("slider", None, min=0, max=100, value=50),
    ),  # <<
    ui.panel_conditional(  # <<
        "input.show && input.kind === 'select'",  # <<
        ui.input_select("select", None, ["A", "B", "C"]),
    ),  # <<
)


def server(input, output, session):
    pass


app = App(app_ui, server)
