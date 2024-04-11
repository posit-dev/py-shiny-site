from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.input_select(
        "select",
        "",
        {
            "1": {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"},
            "2": {"2A": "Choice 2A", "2B": "Choice 2B", "2C": "Choice 2C"},
        },
    ),
    ui.output_text("value"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
