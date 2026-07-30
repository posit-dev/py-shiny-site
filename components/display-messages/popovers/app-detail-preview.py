from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.popover(
        ui.input_action_button("btn", "A button with a popover"),
        "A message inside the popover.",
        title="A popover",
        id="btn_popover",
        placement="right",
    ),
    ui.output_code("popover_state"),
    class_="pt-3",
)


def server(input, output, session):
    @render.code
    def popover_state():
        return f"Popover state: {input.btn_popover()}"


app = App(app_ui, server)
