from enum import Enum

import polars as pl


class Option(str, Enum):
    YEAR = "year"
    MONTH = "month"
    HOUR = "hour"
    DATE = "date"


options = [Option.DATE.value, Option.YEAR.value, Option.MONTH.value, Option.HOUR.value]


def form_filename(keys: list[str], on: list[str]) -> str:
    filename = "__".join(sorted(keys))
    filename = f"data/{filename}.parquet"

    return filename


def persist_data_bitmask(data: pl.DataFrame, by: list[str], on: list[str]) -> None:
    n_cols = len(by)

    for i in range(1, (1 << n_cols)):
        keys = []
        for j in range(i):
            if (i & (1 << j)) != 0:
                keys.append(by[j])

        grouped = data.drop_nulls(subset=by).group_by(keys).agg(pl.col(on).sum())

        grouped.write_parquet(form_filename(keys=keys, on=on))
