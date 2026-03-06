from shiny.express import ui

with ui.layout_column_wrap(width=1/2, height="300px"):
    with ui.card(full_screen=True):
        ui.card_header("Card 1")
        "Content for card 1"

    with ui.card(full_screen=True):
        ui.card_header("Card 2")
        "Content for card 2"
