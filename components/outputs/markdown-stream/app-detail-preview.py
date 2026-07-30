import asyncio

from shiny import App, reactive, ui

chunks = [
    "## Hello, **markdown stream**! \n\n",
    "This content arrives ",
    "one chunk at a time, ",
    "like the response from an LLM. \n\n",
    "- Supports *markdown* formatting \n",
    "- Auto-scrolls as content arrives \n",
]

app_ui = ui.page_fluid(
    ui.input_action_button("stream", "Stream markdown", class_="mb-3"),
    ui.output_markdown_stream("md_stream"),
    class_="px-3 pt-3",
)


def server(input, output, session):
    md = ui.MarkdownStream("md_stream")

    async def chunk_generator():
        for chunk in chunks:
            await asyncio.sleep(0.25)
            yield chunk

    @reactive.effect
    @reactive.event(input.stream)
    async def _():
        await md.stream(chunk_generator())


app = App(app_ui, server)
