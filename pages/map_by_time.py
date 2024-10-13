import polars as pl
import streamlit as st

from common import options

st.title("Crash map by time.")

data_load_state = st.text("Loading data...")
clean_data = pl.read_parquet("data/clean_map.parquet")
data_load_state.text("Loading data...done!")


option = st.selectbox(label="Time to filter by", options=options)


st.subheader(f"Map by {option}")
time = st.slider(
    option,
    clean_data.select(pl.min(option)).row(0)[0],
    clean_data.select(pl.max(option)).row(0)[0],
    int(clean_data.select(pl.median(option)).row(0)[0]),
)
map_state = st.subheader(f"Loading crashes at {option}: {time}...")
filtered_data = clean_data.filter(pl.col(option).eq(time))

st.map(filtered_data.select(["latitude", "longitude"]))
del clean_data
del filtered_data

map_state.subheader(f"Loaded crashes at {option}: {time}!")
