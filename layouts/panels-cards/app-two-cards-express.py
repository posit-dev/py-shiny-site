from shiny.express import ui

with ui.layout_column_wrap(width=1/2, height="300px"):
    with ui.card(full_screen=True):
        ui.card_header("Card 1")
        ui.p("Card 1 body")
        ui.input_slider("slider", "Slider", 0, 10, 5)

    with ui.card(full_screen=True):
        ui.card_header("Card 2")
        ui.p("Card 2 body")
        ui.input_text("text", "Add text", "")
