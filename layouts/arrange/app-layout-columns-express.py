from shiny.express import ui

ui.page_opts(fillable=True)

"ui.layout_columns()"

with ui.layout_columns():
    with ui.card():
        "Card 1"
    with ui.card():
        "Card 2"
    with ui.card():
        "Card 3"
