from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("login", "Login to database")


@reactive.effect
@reactive.event(input.login)
def show_login_modal():
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
def connect_to_databaset():  # <<
    ui.modal_remove()  # <<
    # Code to connect with input.name() and input.password() #<<
