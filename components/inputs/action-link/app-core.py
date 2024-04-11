from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_link("action_link", "Increase Number"),  # <<
    ui.output_text("counter"),
)


def server(input, output, session):
    count = reactive.value(0)

    @reactive.effect
    @reactive.event(input.action_link)  # <<
    def _():
        count.set(count() + 1)

    @render.text()
    def counter():
        return f"{count()}"


app = App(app_ui, server)
