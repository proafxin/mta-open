from os.path import splitext

from dagster import asset
from polars import read_csv

from workflow.assets.constants import DATADIR, OUTDIR, VEHICLE_CRASH_FILENAME


@asset
def vehicle_crash_data() -> None:
    """The dataframe with vehicle crash data. Sourced from MTA Open."""

    file = DATADIR / VEHICLE_CRASH_FILENAME
    data = read_csv(file)
    filename, _ = splitext(VEHICLE_CRASH_FILENAME)
    parquet_file = f"{filename}.parquet"
    data.write_parquet(OUTDIR / parquet_file)
