from faicons import icon_svg
from shiny import reactive
from shiny.express import input, render, ui

with ui.card(full_screen=True):
    ui.card_header("Message Composer")

    with ui.layout_columns(col_widths=[6, 6]):
        ui.input_submit_textarea(
            "message",
            label="Message",
            placeholder="Compose your message...",
            rows=6,
            toolbar=ui.toolbar(
                ui.toolbar_input_select(
                    "priority",
                    label="Priority",
                    choices={"low": "Low", "medium": "Medium", "high": "High"},
                    selected="medium",
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
        )

        with ui.div():
            ui.h5("Sent Messages")

            @render.ui
            def messages_output():
                msg_list = messages.get()
                if not msg_list:
                    return ui.p("No messages sent yet.", style="color: #888;")

                items = []
                for msg in reversed(msg_list):
                    items.append(
                        ui.div(
                            ui.strong(f"{msg['priority'].title()} Priority"),
                            ui.br(),
                            ui.span(msg["text"]),
                            style="padding: 8px; margin-bottom: 8px; border: 1px solid #ddd; border-radius: 4px; display: block;",
                        )
                    )
                return ui.div(*items)


messages = reactive.value([])


@reactive.effect
@reactive.event(input.message)
def _():
    message_text = input.message()
    priority = input.priority()
    if message_text and message_text.strip():
        current = list(messages.get())
        current.append({"text": message_text, "priority": priority})
        messages.set(current)
