from shiny.express import ui

with ui.card():
    ui.card_header("Popover Placement Options")
    with ui.div(
        class_="d-flex flex-wrap justify-content-center align-items-center gap-4",
        style="padding-top: 110px; padding-bottom: 110px;",
    ):
        with ui.popover(title="Top Placement", placement="top"):
            ui.input_action_button(
                "btn_top", "Top", class_="btn-primary", style="min-width: 110px;"
            )
            "Popover content positioned at the top."

        with ui.popover(title="Bottom Placement", placement="bottom"):
            ui.input_action_button(
                "btn_bottom", "Bottom", class_="btn-info", style="min-width: 110px;"
            )
            "Popover content positioned at the bottom."

        with ui.popover(title="Left Placement", placement="left"):
            ui.input_action_button(
                "btn_left", "Left", class_="btn-warning", style="min-width: 110px;"
            )
            "Popover content positioned on the left."

        with ui.popover(title="Right Placement", placement="right"):
            ui.input_action_button(
                "btn_right", "Right", class_="btn-success", style="min-width: 110px;"
            )
            "Popover content positioned on the right."
