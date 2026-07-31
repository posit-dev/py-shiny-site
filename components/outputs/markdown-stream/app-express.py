import asyncio

from shiny import reactive
from shiny.express import input, ui

chunks = [
    "## Hello, **markdown stream**! \n\n",
    "This content arrives ",
    "one chunk at a time, ",
    "like the response from an LLM. \n\n",
    "- Supports *markdown* formatting \n",
    "- Auto-scrolls as content arrives \n",
]

ui.input_action_button("stream", "Stream markdown", class_="mb-3")

md = ui.MarkdownStream("md_stream")  # <<
md.ui()  # <<


async def chunk_generator():
    for chunk in chunks:
        await asyncio.sleep(0.25)
        yield chunk


@reactive.effect
@reactive.event(input.stream)
async def _():
    await md.stream(chunk_generator())
