import polars as pl
import streamlit as st

from common import options

st.title("Crash counts by time")


data_time = pl.read_parquet("data/time_only.parquet")

option = st.selectbox(label="Time to filter by", options=options)
load_state = st.text(f"Loading by {option}")
st.bar_chart(data=data_time[option].value_counts(), x=option, y="count", color=option)

del data_time
