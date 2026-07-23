from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.popover(  # <<
        ui.input_action_button("btn", "Click for popover"),  # <<
        "A popover provides additional context and interactive elements.",  # <<
        title="Popover Title",  # <<
        id="btn_popover",  # <<
        placement="right",  # <<
    ),  # <<
    ui.output_text_verbatim("text"),
)


def server(input, output, session):
    @render.text
    def text():
        return f"Popover open state: {input.btn_popover()}"  # <<


app = App(app_ui, server)
