from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.popover(  # <<
        ui.input_action_button("btn", "Click for popover", class_="btn-primary"),
        {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
        "A popover message with extra detail.",  # <<
        title="Popover Title",  # <<
        id="btn_popover",  # <<
        placement="top",  # <<
    ),
)


def server(input, output, session):
    @render.text
    def text():
        return f"Popover state: {input.btn_popover()}"  # <<


app = App(app_ui, server)
