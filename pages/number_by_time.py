import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

from common import options  # noqa: E402

st.title("Number of crashes by time")

data_time = pl.read_parquet("data/time_only.parquet")
""
st.subheader("Number of crashes in whole New York by date range")
date_counts = data_time["date"].value_counts(sort=True)
date_min = data_time["date"].min()
date_max = data_time["date"].max()
start_date, end_date = st.slider("Choose date", min_value=date_min, max_value=date_max, value=(date_min, date_max))  # type: ignore [type-var]
data_filtered = date_counts.filter(pl.col("date") <= end_date)  # type: ignore [operator]
data_filtered = data_filtered.filter(pl.col("date") >= start_date)  # type: ignore [operator]
st.line_chart(data_filtered, x="date", y="count")
""


option = st.selectbox(label="Time to filter by", options=options)
load_state = st.text(f"Loading by {option}")
st.bar_chart(data=data_time[option].value_counts(), x=option, y="count", color=option)
