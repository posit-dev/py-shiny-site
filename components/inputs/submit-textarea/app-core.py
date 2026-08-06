from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_submit_textarea("message", "Enter your message:"),  # <<
    ui.output_code("value"),
)


def server(input, output, session):
    @render.code
    def value():
        if "message" in input:
            return f"You submitted: {input.message()}"
        return "Nothing submitted yet."


app = App(app_ui, server)
