from shiny import App, ui

app_ui = ui.page_fluid(
    ui.navset_card_underline(
        ui.nav_spacer(),
        ui.nav_panel(
            "Overview",
            "This project has 3 milestones and 12 tasks.",
            ui.br(),
            "Current status: On track",
        ),
        ui.nav_panel(
            "Team",
            ui.tags.ul(
                ui.tags.li("Alice (Lead)"),
                ui.tags.li("Bob (Developer)"),
                ui.tags.li("Carol (Designer)"),
            ),
        ),
        ui.nav_panel(
            "Timeline",
            "Start: January 2026",
            ui.br(),
            "Expected completion: June 2026",
        ),
        title="Project Dashboard",
    ),
    full_screen=True,
    height="300px",
)


def server(input, output, session):
    pass


app = App(app_ui, server)
