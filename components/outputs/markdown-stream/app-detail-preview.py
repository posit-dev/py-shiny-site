import asyncio
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.h4("Markdown Streaming Demo"),
    ui.p("Click the button to see content stream in real-time, perfect for AI/LLM responses."),
    ui.input_action_button("stream", "Stream Content"),
    ui.output_markdown_stream("markdown_output"),
)

def server(input, output, session):
    @render.markdown_stream
    @ui.event(input.stream)
    async def markdown_output():
        content = [
            "## Streaming Response\n\n",
            "This simulates an AI assistant response ",
            "that arrives **incrementally**.\n\n",
            "### Features\n\n",
            "- Real-time rendering\n",
            "- Markdown formatting\n",
            "- Code blocks:\n\n",
            "```python\n",
            "def hello():\n",
            "    print('world')\n",
            "```\n\n",
            "Perfect for chat interfaces!",
        ]
        for chunk in content:
            yield chunk
            await asyncio.sleep(0.2)

app = App(app_ui, server)
