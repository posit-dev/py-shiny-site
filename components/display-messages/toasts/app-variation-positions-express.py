from shiny import reactive
from shiny.express import input, ui

ui.h4("Toast Positions")
ui.input_action_button("top_left", "Top Left")
ui.input_action_button("top_center", "Top Center")
ui.input_action_button("top_right", "Top Right")
ui.input_action_button("bottom_left", "Bottom Left")
ui.input_action_button("bottom_right", "Bottom Right")

@reactive.effect
@reactive.event(input.top_left)
def _():
    ui.show_toast(ui.toast("Top left position", position="top-left"))

@reactive.effect
@reactive.event(input.top_center)
def _():
    ui.show_toast(ui.toast("Top center position", position="top-center"))

@reactive.effect
@reactive.event(input.top_right)
def _():
    ui.show_toast(ui.toast("Top right position", position="top-right"))

@reactive.effect
@reactive.event(input.bottom_left)
def _():
    ui.show_toast(ui.toast("Bottom left position", position="bottom-left"))

@reactive.effect
@reactive.event(input.bottom_right)
def _():
    ui.show_toast(ui.toast("Bottom right position", position="bottom-right"))
