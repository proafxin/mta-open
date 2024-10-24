from datetime import date
from enum import Enum

import polars as pl


def form_mapfilename(cols: list[str]) -> str:
    filename = f"""data/maps/{"__".join([col.lower().strip().replace(" ", "_") for col in cols])}.parquet"""

    return filename


class Option(str, Enum):
    YEAR = "year"
    MONTH = "month"
    HOUR = "hour"
    DATE = "date"


class Incident(str, Enum):
    CRASH = "Number of crash"
    KILLED = "Number of persons killed"
    INJURED = "Number of persons injured"


options = [Option.DATE.value, Option.YEAR.value, Option.MONTH.value, Option.HOUR.value]


def form_filename(keys: list[str], on: list[str]) -> str:
    filename = "__".join(sorted(keys))
    filename = f"data/{filename}.parquet"

    return filename


def persist_data_bitmask(data: pl.DataFrame, by: list[str], on: list[str]) -> None:
    n_cols = len(by)

    for i in range(1, (1 << n_cols)):
        keys = []
        for j in range(n_cols):
            if (i & (1 << j)) != 0:
                keys.append(by[j])

        grouped = (
            data.drop_nulls(subset=keys)
            .group_by(keys)
            .agg(pl.col(on).sum(), pl.col(on[0]).count().alias("number_of_crash"))
        )
        grouped = grouped.sort(by=keys)

        grouped.write_parquet(form_filename(keys=keys, on=on))


MINIMUMS = {"date": date(day=1, month=7, year=2012), "year": 2012, "month": 1, "hour": 0}
MAXIMUMS = {"date": date(day=8, month=10, year=2024), "year": 2024, "month": 12, "hour": 23}
MEDIANS = {"date": date(day=1, month=7, year=2014), "year": 2014, "month": 7, "hour": 12}
NY_CENTER = (40.71261963846181, -73.95064260553615)
