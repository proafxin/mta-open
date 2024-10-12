from os.path import splitext

import duckdb
from dagster import asset
from polars import read_csv

from cleaner import sanitize
from workflow.assets.constants import DATADIR, DUCKDB_LOCATION, OUTDIR, VEHICLE_CRASH_FILENAME

PARQUET_FILE = ""


@asset
def vehicle_crash_raw() -> None:
    """The dataframe with vehicle crash data. Sourced from MTA Open."""

    file = DATADIR / VEHICLE_CRASH_FILENAME
    data = read_csv(file)
    clean_columns = [sanitize(text=column, lower=True) for column in data.columns]
    data.columns = clean_columns
    filename, _ = splitext(VEHICLE_CRASH_FILENAME)
    parquet_file = f"{filename}.parquet"
    PARQUET_FILE = OUTDIR / parquet_file
    data.write_parquet(PARQUET_FILE)


@asset(deps=["vehicle_crash_raw"])
def vehicle_crash() -> None:
    """
    The vehicle crash dataframe, loaded into a DuckDB database
    """
    sql_query = "create or replace table vehicle_crash as (select * from 'workflow/assets/data/vehicle_crash.parquet');"

    conn = duckdb.connect(DUCKDB_LOCATION)
    conn.execute(sql_query)
