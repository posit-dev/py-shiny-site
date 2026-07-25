from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn_show", "Show popover", class_="mt-3 me-3"),
    ui.input_action_button("btn_close", "Close popover", class_="mt-3 me-3"),
    ui.br(),
    ui.popover(
        ui.input_action_button(
            "btn_w_popover", "A button with a popover", class_="mt-3"
        ),
        "A message inside the popover.",
        title="A popover",
        id="btn_popover",
    ),
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.btn_show)
    def show_popover():
        ui.update_popover("btn_popover", show=True)  # <<

    @reactive.effect
    @reactive.event(input.btn_close)
    def close_popover():
        ui.update_popover("btn_popover", show=False)  # <<


app = App(app_ui, server)
