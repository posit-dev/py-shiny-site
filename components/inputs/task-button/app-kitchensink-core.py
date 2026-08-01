from faicons import icon_svg

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_task_button(
        "task_button",
        "Run task",
        icon=icon_svg("play"),
        label_busy="Crunching numbers...",
        icon_busy=icon_svg("spinner"),
        width="300px",
        type="warning",
        auto_reset=False,
        class_="mt-3",
    ),
    ui.input_action_button("reset", "Reset task button"),
    ui.output_code("result"),
)


def server(input, output, session):
    @render.code
    @reactive.event(input.task_button)
    def result():
        return f"Task completed {input.task_button()} time(s)"

    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_task_button("task_button", state="ready")


app = App(app_ui, server)
