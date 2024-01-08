# FIXME: Rewrite to Express
from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("login", "Login"),
)


def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.login)
    def _():
        m = ui.modal(
            ui.input_text("name", "Username:"),  #<<
            ui.input_password("password", "Password:"),  #<<
            ui.input_action_button("connect", "Connect"),  #<<
            easy_close=True,  #<<
            footer=None,  #<<
        )
        ui.modal_show(m)

    @reactive.Effect  #<<
    @reactive.event(input.connect)  #<<
    def __():  #<<
        ui.modal_remove()  #<<
        # Code to connect with input.name() and input.password() #<<


app = App(app_ui, server)
