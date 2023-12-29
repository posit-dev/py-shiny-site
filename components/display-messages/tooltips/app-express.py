# FIXME: Rewrite as an Express app
from shiny import App, render, ui

app_ui = ui.page_fluid(
  ui.tooltip( #<<
      ui.input_action_button("btn", "A button with a tooltip"),
      "A message", #<<
      id="btn_tooltip", #<<
      placement="right" #<<
  ),
    ui.output_text_verbatim("text")
)

def server(input, output, session):
  @render.text
  def text():
      return input.btn_tooltip() #<<

app = App(app_ui, server)
