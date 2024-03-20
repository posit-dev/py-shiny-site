import asyncio
import datetime

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.p("The time is ", ui.output_text("current_time", inline=True)),
    ui.hr(),
    ui.input_task_button("btn", "Square 5 slowly"),
    ui.output_text("sq"),
)


def server(input: Inputs, output: Outputs, session: Session):

    @render.text
    def current_time():
        reactive.invalidate_later(1)
        return datetime.datetime.now().strftime("%H:%M:%S %p")

    @ui.bind_task_button(button_id="btn")
    @reactive.extended_task
    async def sq_value(x):
        await asyncio.sleep(2)
        return x**2

    @reactive.effect
    @reactive.event(input.btn)
    def btn_click():
        sq_value(5)

    @render.text
    def sq():
        return f"5 squared is: {str(sq_value.result())}"


app = App(app_ui, server)
