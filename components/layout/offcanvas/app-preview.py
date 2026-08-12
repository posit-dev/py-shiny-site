from shiny import App, ui

app_ui = ui.page_fillable(
    ui.offcanvas(
        ui.p("Secondary content lives here, out of the way until you need it."),
        title="Details",
        trigger=ui.input_action_button("open", "Open panel"),
        id="panel",
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
