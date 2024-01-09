import asyncio

from shiny import reactive, render
from shiny.express import input, ui

ui.input_action_button("do_compute", "Compute")


@render.ui
@reactive.event(input.do_compute)
async def compute():
    with ui.Progress(min=1, max=15) as p:
        p.set(message="Calculation in progress", detail="This may take a while...")

        for i in range(1, 15):
            p.set(i, message="Computing")
            await asyncio.sleep(0.1)

    return "Done computing!"
