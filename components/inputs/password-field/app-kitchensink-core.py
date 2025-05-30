from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fluid(
    # Card container
    ui.card(
        ui.card_header("Password Input Example"),
        # Create password input
        ui.input_password(
            id="pwd",
            label="Enter Password",
            value="default123",
            width="300px",
            placeholder="Type your password here",
        ),
        # Checkbox to show/hide password
        ui.input_checkbox(
            id="show_password",
            label="Show actual password",
            value=False,
        ),
        # Output for password length
        ui.output_text("password_length"),
        # Output for masked password
        ui.output_text("password_masked"),
    )
)


# Define the server
def server(input, output, session):
    # Show current input length
    @render.text
    def password_length():
        pwd = input.pwd()
        if not pwd:
            return "No password entered"
        return f"Password length: {len(pwd)} characters"

    # Show masked or actual password based on checkbox
    @render.text
    def password_masked():
        pwd = input.pwd()
        if not pwd:
            return ""

        if input.show_password():
            return f"Password: {pwd}"
        else:
            return f"Masked password: {'*' * len(pwd)}"


# Create and return the app
app = App(app_ui, server)
