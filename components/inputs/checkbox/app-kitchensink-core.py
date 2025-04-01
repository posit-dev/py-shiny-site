from shiny import App, reactive, render, ui

# Define the UI
app_ui = ui.page_fluid(
    # Card containing all elements
    ui.card(
        ui.card_header("Checkbox Demo"),
        # Basic checkbox with default value (False)
        ui.input_checkbox(id="basic", label="Basic checkbox"),
        ui.output_text("basic_value"),  # Individual output for basic checkbox
        
        # Checkbox with initial value set to True
        ui.input_checkbox(
            id="preset_value", label="Checkbox with preset value", value=True
        ),
        ui.output_text("preset_value_text"),  # Individual output for preset checkbox
        
        # Checkbox with custom width
        ui.input_checkbox(
            id="custom_width",
            label="Checkbox with custom width (300px)",
            value=False,
            width="300px",
        ),
        ui.output_text("custom_width_text")  # Individual output for custom width checkbox
    )
)


# Define the server
def server(input, output, session):
    @render.text
    def basic_value():
        return f"Value: {input.basic()}"
    
    @render.text
    def preset_value_text():
        return f"Value: {input.preset_value()}"
    
    @render.text
    def custom_width_text():
        return f"Value: {input.custom_width()}"


# Create the app
app = App(app_ui, server)
