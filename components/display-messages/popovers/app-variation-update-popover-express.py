from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("btn_show", "Show popover", class_="mt-3 me-3")
ui.input_action_button("btn_close", "Close popover", class_="mt-3 me-3")
ui.input_action_button("btn_update", "Replace contents", class_="mt-3 me-3")

with ui.popover(id="btn_popover", title="A popover"):
    ui.input_action_button("btn_w_popover", "A button with a popover", class_="mt-3")
    "A message inside the popover."


@reactive.effect
@reactive.event(input.btn_show)
def show_popover():
    ui.update_popover("btn_popover", show=True)  # <<


@reactive.effect
@reactive.event(input.btn_close)
def close_popover():
    ui.update_popover("btn_popover", show=False)  # <<


@reactive.effect
@reactive.event(input.btn_update)
def replace_popover():
    # Positional arguments replace the body; `title` replaces the header.
    ui.update_popover("btn_popover", "An updated message.", title="An updated popover")  # <<
