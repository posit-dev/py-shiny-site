import asyncio

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("button", "Compute"),
    ui.output_text("compute"),
)

def server(input, output, session):
    @output
    @render.text
    @reactive.event(input.button)
    async def compute():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            for i in range(1, 15):
                p.set(i, message="Computing")
                await asyncio.sleep(0.1)

        return "Done computing!"

app = App(app_ui, server)
