from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_submit_textarea(
        "message",
        "Compose your message:",
        placeholder="Type your message here and press Ctrl+Enter or click the submit button...",
    ),
    ui.output_text_verbatim("message_output"),
)

def server(input, output, session):
    @render.text
    def message_output():
        if "message" in input:
            return f"You submitted: {input.message()}"
        return "No message submitted yet. Type a message and press Ctrl+Enter to submit."

app = App(app_ui, server)
