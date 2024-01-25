from shiny.express import ui

ui.page_opts(fillable=True)

with ui.layout_columns(col_widths=(2, 4, 6)):
    with ui.card():
        "Card 1"
    with ui.card():
        "Card 2"
    with ui.card():
        "Card 3"
