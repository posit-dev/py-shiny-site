# FIXME: Rewrite as an Express app
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
  ui.input_action_button("action_button", "Action"), #<<
  ui.output_text("counter")
)

def server(input, output, session):
  @render.text()
  @reactive.event(input.action_button)
  def counter():
      return f"{input.action_button()}"

app = App(app_ui, server)
