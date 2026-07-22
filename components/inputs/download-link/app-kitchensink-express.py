from datetime import date

from shiny.express import render, ui

ui.page_opts(full_width=True)

# Add Font Awesome CSS for icons
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
    )
)

with ui.card():
    ui.card_header("Download Link Examples")

    # Basic download link, auto-placed via the `label` argument
    @render.download_link(filename=f"data-{date.today()}.csv", label="Download CSV")
    def download1():
        yield "name,value\n"
        yield "Alice,100\n"
        yield "Bob,200\n"

    ui.br()
    ui.br()

    # Download link with an icon requires an explicit `ui.download_link()` call,
    # since `icon` isn't forwarded by the auto-placed Express link
    ui.download_link(
        id="download2",
        label="Download Report",
        icon=ui.tags.i(class_="fa-solid fa-file-arrow-down"),
    )

    @render.download_link(filename="report.txt")
    def download2():
        yield "Report generated on: "
        yield str(date.today())

    ui.br()
    ui.br()

    # Auto-placed download link with a fixed width
    @render.download_link(filename="fixed-width.txt", width="300px")
    def download3():
        yield "This link has a fixed width via the `width` parameter."
