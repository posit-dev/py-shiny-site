from shiny.express import input, render, ui

ui.input_select(
    "select",
    "Select an option below:",
    {
        "1": {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"},
        "2": {"2A": "Choice 2A", "2B": "Choice 2B", "2C": "Choice 2C"},
    },
)


@render.text
def value():
    return f"{input.select()}"
