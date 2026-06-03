import asyncio
from shiny import reactive
from shiny.express import input, render, ui

ui.input_task_button("process", "Start processing") # <<

@render.text
@reactive.event(input.process)
async def result():
    await asyncio.sleep(2)
    return "Processing complete!"
