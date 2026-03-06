from shiny import reactive
from shiny.express import input, render, ui

messages = reactive.value([])

with ui.card(full_screen=True):
    ui.card_header("Message Composer")
    ui.input_submit_textarea(
        "message",
        label="Message",
        placeholder="Type your message and click submit...",
        rows=4,
    )

with ui.card(full_screen=True):
    ui.card_header("Sent Messages")

    with ui.card_body():
        @render.ui
        def messages_output():
            msg_list = messages.get()
            if not msg_list:
                return ui.p("No messages sent yet.", style="color: #888;")

            return ui.div(
                *[ui.p(f"- {msg}", style="margin: 4px 0;") for msg in reversed(msg_list)]
            )


@reactive.effect
@reactive.event(input.message)
def _():
    message_text = input.message()
    if message_text and message_text.strip():
        current_messages = list(messages.get())
        current_messages.append(message_text)
        messages.set(current_messages)
