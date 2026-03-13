from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header("Text Editor with Formatting Toolbar"),
        ui.card_body(
            ui.div(
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
                    rows=6,
                ),
                class_="d-flex flex-column align-items-center",
                style="max-width: 600px; margin: 0 auto;",
            ),
        ),
        full_screen=True,
        height="300px",
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
