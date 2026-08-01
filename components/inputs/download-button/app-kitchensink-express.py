from datetime import date

from shiny.express import render, ui
from shiny.ui import download_button  # shiny.express.ui has no download_button

ui.page_opts(full_width=True)

ui.head_content(
    ui.tags.link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
    )
)

with ui.layout_column_wrap(width="100%"):
    with ui.card():
        ui.card_header("Download Button Examples")

        # `label` and `width` are supported by the decorator, so Express can
        # auto-place this button.
        @render.download_button(
            filename=lambda: f"basic-{date.today()}.csv",
            label="Basic Download",
            width="200px",
        )
        def download1():
            yield "name,value\n"
            yield "Alice,100\n"
            yield "Bob,200\n"

        # `icon` is not a `render.download_button()` argument, so place the button
        # yourself and wrap the renderer in `ui.hold()` to suppress the button
        # Express would otherwise auto-place alongside it.
        download_button(
            "download2",
            "Download with Icon",
            icon=ui.tags.i(class_="fa-solid fa-file-csv"),
        )

        with ui.hold():

            @render.download_button(filename=lambda: f"with-icon-{date.today()}.csv")
            def download2():
                yield "name,value\n"
                yield "Carol,300\n"
                yield "Dave,400\n"

        # Same for arbitrary HTML attributes such as `class_` and `style`.
        download_button(
            "download3",
            "Styled Download",
            class_="btn-success",
            style="margin-top: 20px;",
        )

        with ui.hold():

            @render.download_button(filename=lambda: f"styled-{date.today()}.csv")
            def download3():
                yield "name,value\n"
                yield "Eve,500\n"
                yield "Frank,600\n"
