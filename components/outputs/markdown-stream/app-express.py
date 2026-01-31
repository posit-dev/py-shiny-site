import asyncio
from shiny.express import input, render, ui

ui.input_action_button("stream", "Start streaming")

@render.markdown_stream # <<
@ui.event(input.stream)
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
