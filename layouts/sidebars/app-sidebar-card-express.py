from shiny.express import ui

with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(bg="#f8f8f8"):
            "Sidebar"

        "Card content"
