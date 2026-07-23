from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Popover Placement Options"),
        ui.div(
            {
                "class": (
                    "d-flex flex-wrap justify-content-center align-items-center gap-4"
                ),
                "style": "padding-top: 110px; padding-bottom: 110px;",
            },
            ui.popover(
                ui.input_action_button(
                    "btn_top", "Top", class_="btn-primary", style="min-width: 110px;"
                ),
                "Popover content positioned at the top.",
                title="Top Placement",
                placement="top",
            ),
            ui.popover(
                ui.input_action_button(
                    "btn_bottom",
                    "Bottom",
                    class_="btn-info",
                    style="min-width: 110px;",
                ),
                "Popover content positioned at the bottom.",
                title="Bottom Placement",
                placement="bottom",
            ),
            ui.popover(
                ui.input_action_button(
                    "btn_left",
                    "Left",
                    class_="btn-warning",
                    style="min-width: 110px;",
                ),
                "Popover content positioned on the left.",
                title="Left Placement",
                placement="left",
            ),
            ui.popover(
                ui.input_action_button(
                    "btn_right",
                    "Right",
                    class_="btn-success",
                    style="min-width: 110px;",
                ),
                "Popover content positioned on the right.",
                title="Right Placement",
                placement="right",
            ),
        ),
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
