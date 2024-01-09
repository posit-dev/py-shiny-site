from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show modal dialog"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        m = ui.modal(
            "This is a somewhat important message.",
            easy_close=True,
            footer=None,
        )
        ui.modal_show(m)


app = App(app_ui, server)
