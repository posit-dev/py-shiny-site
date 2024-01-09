## file: app.py
import asyncio
from pathlib import Path

from shiny import App, reactive, render, ui

appdir = Path(__file__).parent
app_ui = ui.page_fillable(
    ui.include_css(appdir / "styles.css"),
    ui.input_action_button("button", "Compute"),
    ui.output_text("compute"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
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

## file: styles.css
# shiny-notification-panel { max-width: 100%; }
