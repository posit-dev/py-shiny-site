from faicons import icon_svg
from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Header",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="action1",
                    label="Refresh",
                    icon=icon_svg("arrows-rotate"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_select(
                    id="options",
                    label="Filter",
                    choices=["ABC", "CDE", "EFG"],
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("toolbar_status"),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    @render.text
    def toolbar_status():
        return f"Button clicks: {input.action1()}, Selected: {input.options()}"


app = App(app_ui, server)
