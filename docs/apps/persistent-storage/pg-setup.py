import polars as pl

URI = "postgresql://postgres@localhost:5432/template1"
TABLE_NAME = "testapp"

SCHEMA = {"name": pl.Utf8, "checkbox": pl.Boolean, "favorite_number": pl.Int32}


def load_data():
    return pl.read_database_uri(f"SELECT * FROM {TABLE_NAME}", URI)


def save_info(info: dict):
    new_row = pl.DataFrame(info, schema=SCHEMA)
    new_row.write_database(TABLE_NAME, URI, if_table_exists="append")


def append_info(d: pl.DataFrame, info: dict):
    return pl.concat([d, pl.DataFrame(info, schema=SCHEMA)], how="vertical")
