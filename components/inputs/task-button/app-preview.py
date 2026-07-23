from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_task_button("task_button", "Run Task"),
    ui.output_text("result"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    @output
    @render.text
    @reactive.event(input.task_button)
    def result():
        return ""


app = App(app_ui, server)
