import time

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.row(
        ui.column(4, ui.input_task_button("run", "Run task", auto_reset=False)),
        ui.column(4, ui.input_action_button("reset", "Reset task button")),
        ui.column(4, ui.output_code("result")),
        {"class": "vh-100 justify-content-center align-items-center px-5"},
    ).add_class("text-center")
)


def server(input, output, session):
    @render.code
    @reactive.event(input.run)
    def result():
        time.sleep(1.5)  # Simulate a long-running task
        return f"Ran {input.run()} time(s)"

    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_task_button("run", state="ready")


app = App(app_ui, server)
