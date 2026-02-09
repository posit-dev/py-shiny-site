from faicons import icon_svg
from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Document Actions",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="label_only",
                    label="Label Only",
                ),
                ui.toolbar_input_button(
                    id="icon_and_label",
                    label="Icon + Label",
                    icon=icon_svg("download"),
                    show_label=True,
                ),
                ui.toolbar_input_button(
                    id="icon_only",
                    label="Icon Only",
                    icon=icon_svg("floppy-disk"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("button_status"),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    @render.text
    def button_status():
        return f"Buttons clicked - Label: {input.label_only()}, Icon: {input.icon_only()}, Both: {input.icon_and_label()}"


app = App(app_ui, server)
