from shiny.express import ui

ui.page_opts(fillable=True)

"ui.layout_column_wrap()"

with ui.layout_column_wrap():
    with ui.card():
        "Card 1"
    with ui.card():
        "Card 2"
    with ui.card():
        "Card 3"
