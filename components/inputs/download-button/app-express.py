from datetime import date
from shiny.express import render

@render.download_button(filename=lambda: f"data-{date.today()}.csv") # <<
def download_data():
    yield "name,value\n"
    yield "Alice,100\n"
    yield "Bob,200\n"
