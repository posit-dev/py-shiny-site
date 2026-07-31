import asyncio
from datetime import datetime

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.markdown("The clock keeps ticking while the task runs:"),
    ui.output_code("current_time"),
    ui.input_numeric("x", "x", 1),
    ui.input_numeric("y", "y", 2),
    ui.input_task_button("compute", "Compute, slowly"),
    ui.input_action_button("cancel", "Cancel"),
    ui.output_code("result"),
)


def server(input, output, session):
    @render.code
    def current_time():
        reactive.invalidate_later(1)
        return datetime.now().strftime("%H:%M:%S")

    @ui.bind_task_button(button_id="compute")
    @reactive.extended_task
    async def slow_compute(a: int, b: int) -> int:
        await asyncio.sleep(3)
        return a + b

    @reactive.effect
    @reactive.event(input.compute)
    def _():
        slow_compute(input.x(), input.y())

    @reactive.effect
    @reactive.event(input.cancel)
    def _():
        slow_compute.cancel()

    @render.code
    def result():
        return str(slow_compute.result())


app = App(app_ui, server)
