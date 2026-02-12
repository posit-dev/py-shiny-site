import asyncio
from shiny import ui, render, reactive, App

app_ui = ui.page_fluid(
    ui.input_task_button("process", "Start processing"), # <<
    ui.output_text_verbatim("result"),
)

def server(input, output, session):
    @render.text
    @reactive.event(input.process)
    async def result():
        await asyncio.sleep(2)
        return "Processing complete!"

app = App(app_ui, server)
