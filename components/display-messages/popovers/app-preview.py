from shiny import App, ui

app_ui = ui.page_fluid(
    ui.popover(  # <<
        ui.input_action_button("btn", "Show popover", class_="btn-primary"),
        {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
        "A popover with more information.",  # <<
        title="A popover",  # <<
        id="btn_popover",  # <<
        placement="top",  # <<
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
