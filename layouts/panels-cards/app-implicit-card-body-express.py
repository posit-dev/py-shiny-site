from shiny.express import ui

with ui.card():
    ui.card_header("A header", class_="bg-dark")
    ui.markdown("Some text with a [link](https://github.com).")
