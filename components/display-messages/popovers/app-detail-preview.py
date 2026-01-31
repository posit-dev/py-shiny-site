from shiny import ui, App

app_ui = ui.page_fluid(
    ui.h4("Popover Examples"),
    ui.popover(
        ui.input_action_button("btn1", "Hover or click me"),
        ui.div(
            ui.strong("Popover Title"),
            ui.p("This popover contains rich content including formatted text and multiple paragraphs."),
            ui.p("Click outside to dismiss."),
        ),
        placement="right",
    ),
    ui.br(), ui.br(),
    ui.popover(
        ui.span("Hover over this text", class_="text-primary"),
        "Quick info appears on hover",
        placement="top",
    ),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
