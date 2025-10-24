from datetime import datetime

import polars as pl

DATA_BUCKET = "s3://my-bucket/data/"
STORAGE_OPTIONS = {
    "aws_access_key_id": "<secret>",
    "aws_secret_access_key": "<secret>",
    "aws_region": "us-east-1",
}

SCHEMA = {
    "name": pl.Utf8,
    "checkbox": pl.String,
    "favorite_number": pl.Int32,
    "date": pl.Datetime,
}


def load_data():
    return pl.read_parquet(
        f"{DATA_BUCKET}**/*.parquet", storage_options=STORAGE_OPTIONS
    )


def save_info(info: dict):
    info["date"] = datetime.now()
    new_row = pl.DataFrame(info, schema=SCHEMA)
    new_row.write_parquet(
        f"{DATA_BUCKET}", partition_by="date", storage_options=STORAGE_OPTIONS
    )


def append_info(d: pl.DataFrame, info: dict):
    info["date"] = datetime.now()
    return pl.concat([d, pl.DataFrame(info, schema=SCHEMA)], how="vertical")
