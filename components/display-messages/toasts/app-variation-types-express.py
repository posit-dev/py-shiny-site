from shiny import reactive
from shiny.express import input, ui

ui.h4("Toast Types")
ui.input_action_button("success", "Success")
ui.input_action_button("info", "Info")
ui.input_action_button("warning", "Warning")
ui.input_action_button("danger", "Danger")

@reactive.effect
@reactive.event(input.success)
def _():
    ui.show_toast(ui.toast("Operation successful!", type="success"))

@reactive.effect
@reactive.event(input.info)
def _():
    ui.show_toast(ui.toast("Here's some information", type="info"))

@reactive.effect
@reactive.event(input.warning)
def _():
    ui.show_toast(ui.toast("Warning: Check your input", type="warning"))

@reactive.effect
@reactive.event(input.danger)
def _():
    ui.show_toast(ui.toast("Error: Operation failed", type="danger"))
