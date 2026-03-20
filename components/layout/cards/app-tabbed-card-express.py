from shiny.express import ui

ui.page_opts(full_screen=True, height="300px")

with ui.navset_card_underline(title="Project Dashboard"):
    ui.nav_spacer()
    with ui.nav_panel("Overview"):
        "This project has 3 milestones and 12 tasks."
        ui.br()
        "Current status: On track"
    with ui.nav_panel("Team"):
        ui.tags.ul(
            ui.tags.li("Alice (Lead)"),
            ui.tags.li("Bob (Developer)"),
            ui.tags.li("Carol (Designer)"),
        )
    with ui.nav_panel("Timeline"):
        "Start: January 2026"
        ui.br()
        "Expected completion: June 2026"
