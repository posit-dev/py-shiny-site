from datetime import date

from shiny.express import render, ui
from shiny.ui import download_link  # shiny.express.ui has no download_link

ui.page_opts(full_width=True)

ui.head_content(
    ui.tags.link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
    )
)

with ui.card():
    ui.card_header("Download Link Examples")

    # Express auto-places the link; `label` sets its text.
    @render.download_link(filename=f"data-{date.today()}.csv", label="Download CSV")
    def download1():
        yield "name,value\n"
        yield "Alice,100\n"
        yield "Bob,200\n"

    # `render.download_link()` has no `icon` argument, so place the link yourself
    # with `shiny.ui.download_link()` and wrap the renderer in `ui.hold()` to
    # suppress the link Express would otherwise auto-place alongside it.
    download_link(
        "download2",
        "Download Report",
        icon=ui.tags.i(class_="fa-solid fa-file-arrow-down"),
    )

    with ui.hold():

        @render.download_link(filename="report.txt")
        def download2():
            yield "Report generated on: "
            yield str(date.today())

    # Auto-placed link with a fixed width.
    @render.download_link(
        filename="fixed-width.txt",
        label="Download Fixed-Width Link",
        width="300px",
    )
    def download3():
        yield "This link has a fixed width via the `width` parameter."
