from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_submit_textarea("message", "Enter your message:"), # <<
    ui.output_text_verbatim("message_output"),
)

def server(input, output, session):
    @render.text
    def message_output():
        if "message" in input:
            return f"You submitted: {input.message()}"
        return "No message submitted yet"

app = App(app_ui, server)
