from datetime import date
from shiny.express import render

@render.download(filename=f"data-{date.today()}.csv") # <<
def download_data():
    yield "name,value\n"
    yield "Alice,100\n"
    yield "Bob,200\n"
