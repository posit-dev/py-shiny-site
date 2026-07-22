from datetime import date

from shiny import App, render, ui

# Create the UI
app_ui = ui.page_fluid(
    # Add Font Awesome CSS in the head
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
        )
    ),
    # Main layout
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Download Button Examples"),
            # Basic button with width parameter
            ui.download_button(id="download1", label="Basic Download", width="200px"),
            ui.br(),  # Add spacing
            # Button with icon
            ui.download_button(
                id="download2",
                label="Download with Icon",
                icon=ui.tags.i(class_="fa-solid fa-file-csv"),
            ),
            ui.br(),  # Add spacing
            # Button with custom class and style attributes
            ui.download_button(
                id="download3",
                label="Styled Download",
                class_="btn-success",
                style="margin-top: 20px;",
            ),
        ),
        width="100%",
    ),
)


# Define the server
def server(input, output, session):
    @render.download_button(filename=lambda: f"basic-{date.today()}.csv")
    def download1():
        yield "name,value\n"
        yield "Alice,100\n"
        yield "Bob,200\n"

    @render.download_button(filename=lambda: f"with-icon-{date.today()}.csv")
    def download2():
        yield "name,value\n"
        yield "Carol,300\n"
        yield "Dave,400\n"

    @render.download_button(filename=lambda: f"styled-{date.today()}.csv")
    def download3():
        yield "name,value\n"
        yield "Eve,500\n"
        yield "Frank,600\n"


# Create and return the app
app = App(app_ui, server)
