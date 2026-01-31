import asyncio
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.h4("Task Button Demo"),
    ui.p("Click the button to start a long-running task. The button will show a spinner while processing."),
    ui.input_task_button("process", "Start Task"),
    ui.output_text_verbatim("result"),
)

def server(input, output, session):
    @render.text
    @ui.event(input.process)
    async def result():
        await asyncio.sleep(3)
        return f"Task completed at {asyncio.get_event_loop().time():.1f}"

app = App(app_ui, server)
