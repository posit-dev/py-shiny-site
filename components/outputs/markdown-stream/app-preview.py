from shiny import App, ui

app_ui = ui.page_fluid(
    ui.output_markdown_stream(
        "md_stream",
        content="## Hello, **markdown stream**! \n\n"
        "This content arrives one chunk at a time, "
        "like the response from an LLM.",
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
