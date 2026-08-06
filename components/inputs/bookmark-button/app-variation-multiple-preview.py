from starlette.requests import Request

from shiny import App, reactive, ui


# The UI must be a function to ensure that each user restores their own UI values.
def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"]),
        ui.input_bookmark_button("Bookmark (top)", id="bookmark_top"),
        ui.input_bookmark_button("Bookmark (bottom)", id="bookmark_bottom"),
    )


def server(input, output, session):
    # A custom `id` means Shiny no longer bookmarks on click automatically, so
    # exclude the button ids from the saved state and trigger the bookmark yourself.
    session.bookmark.exclude.append("bookmark_top")
    session.bookmark.exclude.append("bookmark_bottom")

    @reactive.effect
    @reactive.event(input.bookmark_top, input.bookmark_bottom)
    async def _():
        await session.bookmark()

    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)


app = App(app_ui, server, bookmark_store="url")
