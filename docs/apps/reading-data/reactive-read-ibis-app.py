import ibis
from shiny.express import render
from shiny import reactive

con = ibis.postgres.connect(user="", password="", host="", port=, database="")
table = con.table("tablename")

def check_last_updated():
    return table.last_updated.max().execute()

# Every 5 seconds, check if the max timestamp has changed
@reactive.poll(check_last_updated, interval_secs=5)
def data():
    return table.execute()

@render.data_frame
def result():
    return data()
