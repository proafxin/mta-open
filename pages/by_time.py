from enum import Enum

import polars as pl
import streamlit as st

from cleaner import sanitize

st.title("Crashes by time")


date_column = "date"
time_column = "time"


data = pl.read_parquet(st.session_state["contents"])
data.columns = [sanitize(column, lower=True) for column in data.columns]

data = data.with_columns(
    pl.col("crash_date").str.to_date(format="%m/%d/%Y").alias(date_column)
)
data = data.with_columns(
    pl.col("crash_time").str.to_time(format="%H:%M").alias(time_column)
)

data = data.with_columns(
    pl.col(date_column).dt.month().alias("month"),
    pl.col(date_column).dt.year().alias("year"),
    pl.col(time_column).dt.hour().alias("hour"),
)


class Option(str, Enum):
    YEAR = "year"
    MONTH = "month"
    HOUR = "hour"


options = [Option.YEAR.value, Option.MONTH.value, Option.HOUR.value]
option = st.selectbox(label="Time to filter by", options=options)
load_state = st.text(f"Loading by {option}")
st.bar_chart(data=data[option].value_counts(), x=option, y="count", color=option)


clean_data = data.drop_nulls(subset=["latitude", "longitude"])
del data


@st.cache_data
def filter_data(option: str, time: int) -> pl.DataFrame:
    filtered_data = clean_data.filter(pl.col(option).eq(time))

    return filtered_data


if st.checkbox("Show Map"):
    st.subheader(f"Map by {option}")
    time = st.slider(
        option,
        clean_data.select(pl.min(option)).row(0)[0],
        clean_data.select(pl.max(option)).row(0)[0],
        int(clean_data.select(pl.median(option)).row(0)[0]),
    )
    map_state = st.subheader(f"Loading crashes at {option}: {time}...")
    filtered_data = filter_data(option=option, time=time)

    st.map(filtered_data.select(["latitude", "longitude"]))
    del clean_data
    del filtered_data

    map_state.subheader(f"Loaded crashes at {option}: {time}!")
