from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Project Overview",
            class_="bg-primary text-white"
        ),
        ui.card_body(
            ui.p("This project analyzes customer data to identify trends and patterns."),
            ui.p("Key metrics include sales volume, customer retention, and market growth."),
        ),
        ui.card_footer(
            ui.tags.button("View Details", class_="btn btn-sm btn-primary"),
            ui.tags.button("Download Report", class_="btn btn-sm btn-outline-secondary ms-2"),
        ),
        full_screen=True
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
