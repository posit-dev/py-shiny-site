from shiny.express import ui

with ui.card(full_screen=True, height="300px"):
    ui.card_header("Project Dashboard")
    with ui.navset_card_underline():
        with ui.nav_panel("Overview"):
            "This project has 3 milestones and 12 tasks."
            ui.p("Current status: On track")
        with ui.nav_panel("Team"):
            ui.tags.ul(
                ui.tags.li("Alice (Lead)"),
                ui.tags.li("Bob (Developer)"),
                ui.tags.li("Carol (Designer)"),
            )
        with ui.nav_panel("Timeline"):
            ui.p("Start: January 2026")
            ui.p("Expected completion: June 2026")
