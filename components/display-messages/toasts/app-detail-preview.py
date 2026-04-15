from shiny import ui, reactive, App

app_ui = ui.page_fluid(
    ui.h4("Toast Examples"),
    ui.input_action_button("show_toast", "Show Toast"),
    ui.input_action_button("show_success", "Show Success"),
    ui.input_action_button("show_warning", "Show Warning"),
)

def server(input, output, session):
    @reactive.effect
    @reactive.event(input.show_toast)
    def _():
        ui.show_toast("This is a default toast message.")

    @reactive.effect
    @reactive.event(input.show_success)
    def _():
        ui.show_toast(
            ui.toast("Operation completed successfully!", type="success")
        )

    @reactive.effect
    @reactive.event(input.show_warning)
    def _():
        ui.show_toast(
            ui.toast("Please review this warning.", type="warning")
        )

app = App(app_ui, server)
