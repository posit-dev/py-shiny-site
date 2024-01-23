from shiny.express import ui

with ui.row():  # <<
    with ui.column(12):  # <<
        ui.card("Card 1")

with ui.row():  # <<
    with ui.column(6):  # <<
        ui.card("Card 2")

    with ui.column(6):  # <<
        ui.card("Card 2")
