from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn_show", "Show popover", class_="mt-3 me-3"),
    ui.input_action_button("btn_close", "Close popover", class_="mt-3 me-3"),
    ui.input_action_button("btn_update", "Replace contents", class_="mt-3 me-3"),
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
        ui.update_popover("btn_popover", show=True)

    @reactive.effect
    @reactive.event(input.btn_close)
    def close_popover():
        ui.update_popover("btn_popover", show=False)

    @reactive.effect
    @reactive.event(input.btn_update)
    def replace_popover():
        # Positional arguments replace the body; `title` replaces the header.
        ui.update_popover(
            "btn_popover", "An updated message.", title="An updated popover"
        )


app = App(app_ui, server)
