from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_submit_textarea(
        "comment",
        "Your comment:",
        placeholder="Type your comment here...",
        rows=2,
        toolbar=[
            ui.input_action_button("clear", "Clear", class_="btn-sm btn-danger"),
            ui.input_action_button("template", "Use template", class_="btn-sm"),
        ],
    ),
    ui.output_code("value"),
    {"class": "p-3 mx-auto"},
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.clear)
    def _():
        ui.update_submit_textarea("comment", value="", focus=True)

    @reactive.effect
    @reactive.event(input.template)
    def _():
        ui.update_submit_textarea(
            "comment",
            value="Thank you for your feedback. We appreciate your input!",
        )

    @render.code
    def value():
        if "comment" in input:
            return f"You submitted: {input.comment()}"
        return "Nothing submitted yet."


app = App(app_ui, server)
