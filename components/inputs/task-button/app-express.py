import asyncio
from shiny.express import input, render, ui

ui.input_task_button("process", "Start processing") # <<

@render.text
@ui.event(input.process)
async def result():
    await asyncio.sleep(2)
    return "Processing complete!"
