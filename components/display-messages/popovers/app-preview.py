from shiny import ui, App

app_ui = ui.page_fluid(
    ui.popover(
        ui.span("Hover over this text", class_="text-primary", style="cursor: help;"),
        "Popover content appears here",
        title="Info",
        placement="top",
        options={"trigger": "hover focus"},
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)

def server(input, output, session):
    pass

app = App(app_ui, server)
