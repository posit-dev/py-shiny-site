from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.tooltip(  # <<
        ui.input_action_button("tooltip", "Show tooltip", class_="btn-primary"),
        {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
        "A tooltip message",  # <<
        id="btn_tooltip",  # <<
        placement="top",  # <<
    ),
)


def server(input, output, session):
    @render.text
    def text():
        return f"Tooltip state: {input.btn_tooltip()}"  # <<


app = App(app_ui, server)
