from shiny import render
from shiny.express import input, ui


ui.input_password("password", "Password", "mypassword1")  # <<


@render.text
def value():
    return input.password()
