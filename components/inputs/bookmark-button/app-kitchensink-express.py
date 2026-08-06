from faicons import icon_svg

from shiny.express import app_opts, session, ui

app_opts(bookmark_store="url")

ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"])
ui.input_bookmark_button(
    "Save my state",
    icon=icon_svg("bookmark"),
    width="300px",
    disabled=False,
    title="Save these inputs and copy a shareable URL.",
    class_="mt-3",
)


# Update the browser's URL in place instead of showing a modal.
@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
