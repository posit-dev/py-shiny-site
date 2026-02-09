from shiny.express import ui

with ui.layout_column_wrap(width=1/3, height="200px"):
    with ui.card(full_screen=True):
        ui.card_header("Sales")
        ui.h3("$45,231")
        ui.p("Up 12% from last month", class_="text-success")

    with ui.card(full_screen=True):
        ui.card_header("Customers")
        ui.h3("2,345")
        ui.p("Up 8% from last month", class_="text-success")

    with ui.card(full_screen=True):
        ui.card_header("Conversion Rate")
        ui.h3("3.2%")
        ui.p("Down 2% from last month", class_="text-danger")
