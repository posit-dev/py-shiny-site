from faicons import icon_svg
from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(fillable=False)

messages = reactive.value([])

with ui.card(full_screen=True, height="250px"):
    ui.card_header("Message Composer")
    with ui.card_body():
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
        )

with ui.card(full_screen=True, height="250px"):
    ui.card_header("Sent Messages")

    with ui.card_body():
        @render.ui
        def messages_output():
            msg_list = messages.get()
            if not msg_list:
                return ui.p("No messages sent yet.", style="color: #888;")

            return ui.div(
                *[
                    ui.p(
                        f"[{msg['priority']}] {msg['text']}",
                        style="margin: 4px 0;",
                    )
                    for msg in reversed(msg_list)
                ]
            )


@reactive.effect
@reactive.event(input.message)
def _():
    message_text = input.message()
    if message_text and message_text.strip():
        current_messages = list(messages.get())
        current_messages.append(
            {"text": message_text, "priority": input.priority()}
        )
        messages.set(current_messages)
