from shiny import reactive
from shiny.express import input, ui, render

ui.page_opts(full_width=True)

with ui.card():
    ui.card_header("Checkbox Demo")

    # Basic checkbox with default value (False)
    ui.input_checkbox(id="basic", label="Basic checkbox")
    
    @render.text
    def basic_value():
        return f"Value: {input.basic()}"

    # Checkbox with initial value set to True
    ui.input_checkbox(id="preset_value", label="Checkbox with preset value", value=True)
    
    @render.text
    def preset_value_text():
        return f"Value: {input.preset_value()}"

    # Checkbox with custom width
    ui.input_checkbox(
        id="custom_width",
        label="Checkbox with custom width (300px)",
        value=False,
        width="300px",
    )
    
    @render.text
    def custom_width_text():
        return f"Value: {input.custom_width()}"
