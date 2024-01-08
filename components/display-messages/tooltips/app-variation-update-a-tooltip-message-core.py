from shiny import App, reactive, ui

app_ui = ui.page_fluid(
  ui.tooltip(
      ui.input_action_button("btn", "A button with a tooltip"),
      "A message",
      id="btn_tooltip",
      placement="right"
  ),
  ui.tags.br(),
  ui.tags.br(),
  ui.input_action_button("btn_update", "Update tooltip message")
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.btn_update)
    def _():
        content = (
            "A " + " ".join(["NEW" for _ in range(input.btn_update())])+ " message"
        )

        ui.update_tooltip("btn_tooltip", content, show=True) #<<

app = App(app_ui, server)
