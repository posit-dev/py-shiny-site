from datetime import date

from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
        )
    ),
    ui.card(
        ui.card_header("Download Link Examples"),
        # Basic download link
        ui.download_link(id="download1", label="Download CSV"),
        ui.br(),
        ui.br(),
        # Download link with an icon
        ui.download_link(
            id="download2",
            label="Download Report",
            icon=ui.tags.i(class_="fa-solid fa-file-arrow-down"),
        ),
        ui.br(),
        ui.br(),
        # Download link with a fixed width
        ui.download_link(id="download3", label="Download Fixed-Width Link", width="300px"),
    ),
)


def server(input, output, session):
    @render.download_link(filename=f"data-{date.today()}.csv")
    def download1():
        yield "name,value\n"
        yield "Alice,100\n"
        yield "Bob,200\n"

    @render.download_link(filename="report.txt")
    def download2():
        yield "Report generated on: "
        yield str(date.today())

    @render.download_link(filename="fixed-width.txt")
    def download3():
        yield "This link has a fixed width via the `width` parameter."


app = App(app_ui, server)
