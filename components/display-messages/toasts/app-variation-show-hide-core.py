from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show toast"),
    ui.input_action_button("hide", "Hide toast"),
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        ui.show_toast(
            ui.toast(
                "This toast stays until you hide it.",
                id="persistent_toast",  # <<
                duration_s=None,
            )
        )

    @reactive.effect
    @reactive.event(input.hide)
    def _():
        ui.hide_toast("persistent_toast")  # <<


app = App(app_ui, server)
