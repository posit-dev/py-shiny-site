from shiny import App, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Sales"),
            ui.card_body(
                ui.h3("$45,231"),
                ui.p("Up 12% from last month", class_="text-success")
            ),
            full_screen=True
        ),
        ui.card(
            ui.card_header("Customers"),
            ui.card_body(
                ui.h3("2,345"),
                ui.p("Up 8% from last month", class_="text-success")
            ),
            full_screen=True
        ),
        ui.card(
            ui.card_header("Conversion Rate"),
            ui.card_body(
                ui.h3("3.2%"),
                ui.p("Down 2% from last month", class_="text-danger")
            ),
            full_screen=True
        ),
        width=1/3,
        height="200px"
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
