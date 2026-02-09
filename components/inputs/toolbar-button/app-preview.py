from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Document Editor",
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
            ui.p("Click the toolbar buttons to perform actions."),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
