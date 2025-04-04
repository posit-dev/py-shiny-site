from shiny.express import input, render, ui

# Set page title
ui.page_opts(full_width=True)

with ui.card():
    ui.card_header("Password Input Example")

    # Create password input
    ui.input_password(
        id="pwd",
        label="Enter Password",
        value="default123",
        width="300px",
        placeholder="Type your password here",
    )

    # Checkbox to show/hide password
    ui.input_checkbox(
        id="show_password",
        label="Show actual password",
        value=False,
    )

    # Show current input length
    @render.text
    def password_length():
        pwd = input.pwd()
        if not pwd:
            return "No password entered"
        return f"Password length: {len(pwd)} characters"

    # Show masked password
    @render.text
    def password_masked():
        pwd = input.pwd()
        if not pwd:
            return ""

        if input.show_password():
            return f"Password: {pwd}"
        else:
            return f"Masked password: {'*' * len(pwd)}"
