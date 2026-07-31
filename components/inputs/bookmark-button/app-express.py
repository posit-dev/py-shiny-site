from shiny.express import app_opts, session, ui

app_opts(bookmark_store="url")

ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"])
ui.input_bookmark_button()  # <<


# Update the browser's URL in place instead of showing a modal.
@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
