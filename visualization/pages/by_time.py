from enum import Enum

import polars as pl
import streamlit as st
from polars import DataFrame

from visualization.components import vehicles_crash_data

st.title("Crashes by time")


date_column = "date"
time_column = "time"


@st.cache_data
def data_with_time() -> DataFrame:
    data = vehicles_crash_data()
    data = data.with_columns(pl.col("crash_date").str.to_date(format="%m/%d/%Y").alias(date_column))
    data = data.with_columns(pl.col("crash_time").str.to_time(format="%H:%M").alias(time_column))

    return data.with_columns(
        pl.col(date_column).dt.month().alias("month"),
        pl.col(date_column).dt.year().alias("year"),
        pl.col(time_column).dt.hour().alias("hour"),
    )


data = data_with_time()


@st.cache_data
def clean_time_data() -> DataFrame:
    return data.drop_nulls(subset=["latitude", "longitude"])


class Option(str, Enum):
    YEAR = "year"
    MONTH = "month"
    HOUR = "hour"


@st.cache_data
def count_by_time(option: str) -> DataFrame:
    return data[option].value_counts()


options = [Option.YEAR.value, Option.MONTH.value, Option.HOUR.value]
option = st.selectbox(label="Time to filter by", options=options)
load_state = st.text(f"Loading by {option}")
st.bar_chart(data=count_by_time(option=option), x=option, y="count", color=option)

clean_data = clean_time_data()

if st.checkbox("Show Map"):
    st.subheader(f"Map by {option}")
    time = st.slider(
        option,
        data.select(pl.min(option)).row(0)[0],
        data.select(pl.max(option)).row(0)[0],
        int(data.select(pl.median(option)).row(0)[0]),
    )
    filtered_data = clean_data.filter(pl.col(option).le(time))

    st.subheader(f"Map of all crashes at {option}: {time}")
    st.map(filtered_data)
