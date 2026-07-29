import gspread
import polars as pl

# Authenticate with Google Sheets using a service account
gc = gspread.service_account(filename="service_account.json")

# Put your URL here
sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/your_workbook_id")
WORKSHEET = sheet.get_worksheet(0)

import polars as pl

# A polars schema that the data should conform to
SCHEMA = {"name": pl.Utf8, "checkbox": pl.String, "favorite_number": pl.Int32}


def load_data():
    return pl.from_dicts(
        WORKSHEET.get_all_records(expected_headers=SCHEMA.keys()), schema=SCHEMA
    )


def save_info(info: dict):
    # Google Sheets expects a list of values for the new row
    new_row = list(info.values())
    WORKSHEET.append_row(new_row, insert_data_option="INSERT_ROWS")


def append_info(d: pl.DataFrame, info: dict):
    # Cast the boolean to a string for storage
    info["checkbox"] = str(info["checkbox"])
    return pl.concat([d, pl.DataFrame(info, schema=SCHEMA)], how="vertical")
