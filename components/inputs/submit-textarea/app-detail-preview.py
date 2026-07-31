from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_submit_textarea(
        "message",
        "Compose your message:",
        placeholder="Type a message, then press Ctrl+Enter or click the button...",
    ),
    ui.output_code("value"),
    {"class": "p-3 mx-auto"},
)


def server(input, output, session):
    @render.code
    def value():
        if "message" in input:
            return f"You submitted: {input.message()}"
        return "Nothing submitted yet."


app = App(app_ui, server)
