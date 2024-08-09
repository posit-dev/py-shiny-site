import asyncio  # <<
import datetime

from shiny import reactive
from shiny.express import render, input, ui


@render.text
def current_time():
    reactive.invalidate_later(1)
    time_str = datetime.datetime.now().strftime("%H:%M:%S %p")
    return f"The time is, {time_str}"


ui.hr()

ui.input_task_button("btn", "Square 5 slowly")  # <<


@ui.bind_task_button(button_id="btn")  # <<
@reactive.extended_task  # <<
async def sq_values(x):  # <<
    await asyncio.sleep(2)  # <<
    return x**2  # <<


@reactive.effect  # <<
@reactive.event(input.btn)  # <<
def btn_click():  # <<
    sq_values(5)  # <<


@render.text
def sq():
    return str(sq_values.result())
