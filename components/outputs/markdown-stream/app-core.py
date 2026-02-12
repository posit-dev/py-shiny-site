import asyncio
from shiny import ui, render, reactive, App

app_ui = ui.page_fluid(
    ui.input_action_button("stream", "Start streaming"),
    ui.output_markdown_stream("markdown_output"), # <<
)

def server(input, output, session):
    @render.markdown_stream
    @reactive.event(input.stream)
    async def markdown_output():
        lines = [
            "# Streaming Content\n\n",
            "This content appears ",
            "**word by word** ",
            "as it streams.\n\n",
            "- First item\n",
            "- Second item\n",
            "- Third item\n",
        ]
        for line in lines:
            yield line
            await asyncio.sleep(0.3)

app = App(app_ui, server)
