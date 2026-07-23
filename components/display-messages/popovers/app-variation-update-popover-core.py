from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn_show", "Show popover", class_="mt-3 me-3"),
    ui.input_action_button("btn_close", "Close popover", class_="mt-3 me-3"),
    ui.br(),
    ui.br(),
    ui.popover(
        ui.input_action_button(
            "btn_w_popover", "A button with a popover", class_="mt-3"
        ),
        "A message inside the popover",
        title="Dynamic Popover",
        id="popover_id",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.btn_show)
    def _():
        ui.update_popover("popover_id", show=True)  # <<

    @reactive.effect
    @reactive.event(input.btn_close)
    def _():
        ui.update_popover("popover_id", show=False)  # <<


app = App(app_ui, server)
