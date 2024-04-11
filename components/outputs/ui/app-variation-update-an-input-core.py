from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.input_radio_buttons(
            "mode", "Display mode", ["Table", "Plot"], selected="Table"
        ),
        ui.output_ui("mode_controls"),
    )
)


def server(input, output, session):
    @render.ui
    def mode_controls():
        if input.mode() == "Table":
            rows = input.rows() if "rows" in input else 10
            cols = input.cols() if "cols" in input else 4
            return ui.TagList(
                ui.input_slider("rows", "Rows:", value=rows, min=1, max=10),
                ui.input_slider("cols", "Columns:", value=cols, min=1, max=10),
            )
        else:
            height = input.height() if "height" in input else 500
            width = input.width() if "width" in input else 500
            return ui.TagList(
                ui.input_slider("height", "Height:", value=height, min=100, max=1000),
                ui.input_slider("width", "Width:", value=width, min=100, max=1000),
            )


app = App(app_ui, server)
