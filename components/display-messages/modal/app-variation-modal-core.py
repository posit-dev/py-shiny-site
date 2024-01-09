from shiny import App, reactive, ui

app_ui = ui.page_fixed(ui.input_action_button("login", "Login to database"))


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.login)
    def _():
        m = ui.modal(  # <<
            ui.input_text("name", "Username:"),
            ui.input_password("password", "Password:"),
            ui.input_action_button("connect", "Connect"),
            title="Database Credentials",  # <<
            easy_close=True,  # <<
            footer=None,  # <<
        )  # <<
        ui.modal_show(m)

    @reactive.effect  # <<
    @reactive.event(input.connect)  # <<
    def __():  # <<
        ui.modal_remove()  # <<
        # Code to connect with input.name() and input.password() #<<


app = App(app_ui, server)
