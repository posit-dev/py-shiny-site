from shiny import ui

ui.page_opts(fillable=True)

with ui.layout_columns():  # <<
    with ui.card():  # <<
        ui.card_header("Card 1 header")
        ui.p("Card 1 body")
        ui.input_slider("slider", "Slider", 0, 10, 5)

    with ui.card():  # <<
        ui.card_header("Card 2 header")
        ui.p("Card 2 body")
        ui.input_text("text", "Add text", "")
