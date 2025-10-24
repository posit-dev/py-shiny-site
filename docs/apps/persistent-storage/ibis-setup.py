import ibis
import polars as pl

# NOTE:  app.py should import CONN and close it via
# `_ = session.on_close(CONN.disconnect)` or similar
CONN = ibis.postgres.connect(
    user="postgres", password="", host="localhost", port=5432, database="template1"
)
TABLE_NAME = "testapp"

SCHEMA = {"name": pl.Utf8, "checkbox": pl.Boolean, "favorite_number": pl.Int32}


def load_data():
    return CONN.table(TABLE_NAME).to_polars()


def save_info(info: dict):
    new_row = pl.DataFrame(info, schema=SCHEMA)
    CONN.insert(TABLE_NAME, new_row, overwrite=False)


def append_info(d: pl.DataFrame, info: dict):
    return pl.concat([d, pl.DataFrame(info, schema=SCHEMA)], how="vertical")
