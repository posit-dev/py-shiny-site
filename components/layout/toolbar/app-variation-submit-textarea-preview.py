from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header("Message Composer"),
        ui.card_body(
            ui.input_submit_textarea(
                "message",
                label="Message",
                placeholder="Compose your message...",
                rows=4,
                toolbar=ui.toolbar(
                    ui.toolbar_input_select(
                        "priority",
                        label="Priority",
                        choices=["Low", "Medium", "High"],
                        selected="Medium",
                        icon=icon_svg("flag"),
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_button(
                        "attach",
                        label="Attach",
                        icon=icon_svg("paperclip"),
                    ),
                    align="right",
                ),
            ),
        ),
        full_screen=True,
        height="250px",
    ),
    ui.card(
        ui.card_header("Sent Messages"),
        ui.card_body(
            ui.p("No messages sent yet.", style="color: #888;"),
        ),
        full_screen=True,
        height="250px",
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
