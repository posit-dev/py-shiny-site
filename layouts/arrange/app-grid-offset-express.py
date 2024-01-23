from shiny.express import ui

with ui.row():
    with ui.column(4):
        ui.card("Card 1")

    with ui.column(4, offset=4):  # <<
        ui.card("Card 2")

with ui.row():
    with ui.column(4, offset=4):  # <<
        ui.card("Card 3")

with ui.row():
    with ui.column(4):  # <<
        ui.card("Card 4")

    with ui.column(4, offset=4):  # <<
        ui.card("Card 5")
