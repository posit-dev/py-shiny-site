from shiny.express import ui

ui.page_opts(fillable=True)

with ui.card():  # <<
    ui.card_header("Card with sidebar")

    with ui.layout_sidebar():  # <<
        with ui.sidebar(bg="#f8f8f8"):  # <<
            "Sidebar"  # <<

        "Card content"  # <<
