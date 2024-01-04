from shiny import App, render, ui

app_ui = ui.page_fluid(
  ui.tooltip(
      ui.input_action_button("btn", "A button with a tooltip"),
      "A message",
      id="btn_tooltip"
  ),
    ui.output_text_verbatim("text"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"}
)

def server(input, output, session):
  @render.text
  def text():
      return ""

app = App(app_ui, server)
