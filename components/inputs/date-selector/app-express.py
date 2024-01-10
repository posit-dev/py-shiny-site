from shiny import render
from shiny.express import input, ui


ui.input_date("date", "Date") #<<


@render.text
def value():
    return input.date()
