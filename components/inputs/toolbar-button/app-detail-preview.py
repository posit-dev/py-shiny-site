from faicons import icon_svg
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Document Editor",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="save",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                ),
                ui.toolbar_input_button(
                    id="edit",
                    label="Edit",
                    icon=icon_svg("pencil"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    id="delete",
                    label="Delete",
                    icon=icon_svg("trash"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.h4("Action Log"),
            ui.output_text_verbatim("action_log"),
        ),
        full_screen=True,
        height="350px",
    )
)


def server(input, output, session):
    actions = reactive.Value([])

    @reactive.effect
    @reactive.event(input.save)
    def _():
        current = actions.get()
        actions.set(current + [f"Saved document (click #{input.save()})"])

    @reactive.effect
    @reactive.event(input.edit)
    def _():
        current = actions.get()
        actions.set(current + [f"Edited document (click #{input.edit()})"])

    @reactive.effect
    @reactive.event(input.delete)
    def _():
        current = actions.get()
        actions.set(current + [f"Deleted document (click #{input.delete()})"])

    @render.text
    def action_log():
        action_list = actions.get()
        if not action_list:
            return "No actions yet. Click a toolbar button."
        return "\n".join(action_list[-5:])  # Show last 5 actions


app = App(app_ui, server)
