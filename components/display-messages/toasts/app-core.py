from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show toast"),
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        ui.show_toast(  # <<
            ui.toast(
                "You have a new message!",
                header=ui.toast_header("Inbox", status="just now"),
                type="success",
                id="message_toast",
            )
        )


app = App(app_ui, server)
