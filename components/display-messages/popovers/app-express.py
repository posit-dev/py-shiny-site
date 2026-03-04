from shiny.express import ui

with ui.popover(title="Popover Title"): # <<
    ui.input_action_button("btn", "Click me")
    "This is a popover with helpful information!"
