from shiny.express import ui

with ui.card(max_height="250px", full_screen=True):
    ui.card_header("A long, scrolling, description")
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 50
