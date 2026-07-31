from starlette.requests import Request

from shiny import App, ui


# The UI must be a function to ensure that each user restores their own UI values.
def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"]),
        ui.input_bookmark_button(),  # <<
    )


def server(input, output, session):
    # Update the browser's URL in place instead of showing a modal.
    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)


app = App(app_ui, server, bookmark_store="url")
