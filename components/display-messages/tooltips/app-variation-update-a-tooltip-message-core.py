from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.tooltip(
        ui.input_action_button("btn", "A button with a tooltip"),
        "A message",
        id="btn_tooltip",
        placement="right",
    ),
    ui.input_text("tooltip_msg", "Tooltip message", "Change me!").add_class("mt-4"),
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.tooltip_msg)
    def update_tooltip_msg():
        ui.update_tooltip("btn_tooltip", input.tooltip_msg(), show=True)


app = App(app_ui, server)
