from shiny import App, ui, render, reactive

USERS = {"admin": "password123", "user": "mypass"}


def login_ui():
    return ui.page_fluid(
        ui.h2("Login"),
        ui.input_text("username", "Username", placeholder="Enter username"),
        ui.input_password("password", "Password", placeholder="Enter password"),
        ui.input_action_button("login_btn", "Login"),
        ui.output_text("login_status"),
        ui.br(),
        ui.card(
            ui.h2("Demo credentials:"),
            ui.div("admin / password123"),
            ui.div("user / mypass"),
        ),
    )


def dashboard_ui():
    return ui.page_fluid(
        ui.h1("Dashboard"),
        ui.output_text("current_user_display"),
        ui.input_action_button("logout_btn", "Logout"),
    )


def server(input, output, session):
    authenticated = reactive.Value(False)
    current_user = reactive.Value("")

    @reactive.Effect
    @reactive.event(input.login_btn)
    def handle_login():
        username = input.username()
        password = input.password()

        if USERS.get(username) == password:
            authenticated.set(True)
            current_user.set(username)
        else:
            authenticated.set(False)
            current_user.set("")

    @reactive.Effect
    @reactive.event(input.logout_btn)
    def handle_logout():
        authenticated.set(False)
        current_user.set("")

    @render.ui
    def dynamic_ui():
        if authenticated():
            return dashboard_ui()
        else:
            return login_ui()

    @render.text
    def login_status():
        if not authenticated() and input.login_btn() > 0:
            return "Invalid credentials. Please try again."
        return ""

    @render.text
    def current_user_display():
        if user := current_user():
            return f"You are logged in as: {user}"
        return ""


app_ui = ui.page_fluid(ui.output_ui("dynamic_ui"))

app = App(app_ui, server)
