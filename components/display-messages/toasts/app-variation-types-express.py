from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("success", "Success")
ui.input_action_button("info", "Info")
ui.input_action_button("warning", "Warning")
ui.input_action_button("danger", "Danger")


@reactive.effect
@reactive.event(input.success)
def show_success():
    ui.show_toast(ui.toast("Operation successful!", type="success"))  # <<


@reactive.effect
@reactive.event(input.info)
def show_info():
    ui.show_toast(ui.toast("Here's some information.", type="info"))


@reactive.effect
@reactive.event(input.warning)
def show_warning():
    ui.show_toast(ui.toast("Warning: check your input.", type="warning"))


@reactive.effect
@reactive.event(input.danger)
def show_danger():
    ui.show_toast(ui.toast("Error: operation failed.", type="danger"))
