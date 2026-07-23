from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("btn_show", "Show popover", class_="mt-3 me-3")
ui.input_action_button("btn_close", "Close popover", class_="mt-3 me-3")

with ui.popover(id="popover_id", title="Dynamic Popover"):
    ui.input_action_button("btn_w_popover", "A button with a popover", class_="mt-3")
    "A message inside the popover"


@reactive.effect
@reactive.event(input.btn_show)
def _():
    ui.update_popover("popover_id", show=True)  # <<


@reactive.effect
@reactive.event(input.btn_close)
def _():
    ui.update_popover("popover_id", show=False)  # <<
