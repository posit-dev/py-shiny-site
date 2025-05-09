from shiny import App, reactive, render, ui

# Define the UI
app_ui = ui.page_fluid(
    # Create a card to contain the input and output
    ui.card(
        ui.card_header("Text Input Demo"),
        # Create text input with all possible parameters
        ui.input_text(
            id="demo_text",  # Required: unique identifier
            label="Demo Text Input",  # Required: label text
            value="Initial value",  # Optional: starting value
            width="300px",  # Optional: CSS width
            placeholder="Enter text here",  # Optional: hint text
            autocomplete="username",  # Optional: browser autocomplete behavior
            spellcheck="true",  # Optional: browser spellcheck behavior
        ),
        # Output area for the current value
        ui.output_text("current_value"),
    )
)


# Define the server function
def server(input, output, session):
    @render.text
    def current_value():
        return f"Current value: {input.demo_text()}"


# Create and return the app object
app = App(app_ui, server)
