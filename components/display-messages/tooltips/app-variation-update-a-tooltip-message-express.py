from shiny import reactive
from shiny.express import input, ui

with ui.tooltip(id="btn_tooltip", placement="right"):
    ui.input_action_button("btn", "A button with a tooltip")
    "The tooltip message"


ui.input_text("tooltip_msg", "Tooltip message", "Change me!").add_class("mt-4")


@reactive.effect()
@reactive.event(input.tooltip_msg)
def update_tooltip_msg():
    ui.update_tooltip("btn_tooltip", input.tooltip_msg(), show=True)
