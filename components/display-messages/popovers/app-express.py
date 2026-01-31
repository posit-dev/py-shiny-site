from shiny.express import ui

ui.popover( # <<
    ui.input_action_button("btn", "Click me"),
    "This is a popover with helpful information!",
    title="Popover Title",
)
