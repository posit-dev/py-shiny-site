from shiny.express import ui

ui.page_opts(fillable=True)

with ui.layout_column_wrap(width="300px"):  # <<
    with ui.card():
        "Card 1"
    with ui.card():
        "Card 2"
    with ui.card():
        "Card 3"
    with ui.card():
        "Card 4"
