import asyncio
import datetime

import matplotlib.pyplot as plt
import numpy as np

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("x", "x", value=5),
    ui.input_task_button("btn", "Square number slowly"),
    ui.output_text("sq"),
    ui.hr(),
    ui.p(
        "While computing, the time updates and you can still interact with the histogram."
    ),
    ui.p("The time is ", ui.output_text("current_time", inline=True)),
    ui.input_slider("n", "Number of observations", min=0, max=1000, value=500),
    ui.output_plot("plot"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.plot(alt="A histogram")
    def plot():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(input.n())
        fig, ax = plt.subplots()
        ax.hist(x, bins=30, density=True)
        return fig

    @render.text
    def current_time():
        reactive.invalidate_later(1)
        return datetime.datetime.now().strftime("%H:%M:%S %p")

    @ui.bind_task_button(button_id="btn")
    @reactive.extended_task
    async def sq_values(x):
        await asyncio.sleep(5)
        return x**2

    @reactive.effect
    @reactive.event(input.btn)
    def btn_click():
        sq_values(input.x())

    @render.text
    def sq():
        return str(sq_values.result())


app = App(app_ui, server)
