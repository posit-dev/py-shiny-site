from shiny.express import input, render, ui

ui.input_password("password", "Password", "mypassword1")  # <<


@render.text
def value():
    return input.password()
