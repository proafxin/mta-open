import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

from common import options  # noqa: E402

st.title("Range queries by time")

data_time = pl.read_parquet("data/time_only.parquet")
""
st.subheader("Number of crashes in New York within date range")
""
option = st.selectbox(label="Time to filter by", options=options)

st.subheader(f"Map by {option}")
minimum = data_time[option].min()  # type: ignore [arg-type]
maximum = data_time[option].max()  # type: ignore [arg-type]
value = (minimum, maximum)
start_time, end_time = st.slider(option.upper(), minimum, maximum, value)  # type: ignore [arg-type, type-var]

boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
selected_boroughs = options = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs)
data_filtered = data_time.filter(pl.col("borough").is_in(selected_boroughs))

value_counts = data_filtered.group_by(["borough", option]).len()
""
st.line_chart(value_counts, x=option, y="len", color="borough")
""
