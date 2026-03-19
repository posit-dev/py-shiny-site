from faicons import icon_svg
from shiny.express import input, render, ui

with ui.card(full_screen=True):
    ui.card_header("Text Editor with Formatting Toolbar")

    with ui.div(class_="d-flex flex-column align-items-center", style="max-width: 600px; margin: 0 auto;"):
        ui.input_text_area(
            "content",
            label=ui.toolbar(
                ui.toolbar_input_button(
                    "bold",
                    label="Bold",
                    icon=icon_svg("bold"),
                ),
                ui.toolbar_input_button(
                    "italic",
                    label="Italic",
                    icon=icon_svg("italic"),
                ),
                ui.toolbar_input_button(
                    "code",
                    label="Code",
                    icon=icon_svg("code"),
                ),
                align="right",
            ),
            placeholder="Type your content here...",
            rows=8,
        )

        @render.text
        def formatting_status():
            return f"Bold: {input.bold()} | Italic: {input.italic()} | Code: {input.code()}"
