import asyncio
from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_task_button("btn", "Fit Model"),
)


def server(input: Inputs, output: Outputs, session: Session):

    @ui.bind_task_button(button_id="btn")
    @reactive.extended_task
    async def long_calculation():
        await asyncio.sleep(1)

    @reactive.effect
    @reactive.event(input.btn)
    def btn_click():
        long_calculation()


app = App(app_ui, server)
