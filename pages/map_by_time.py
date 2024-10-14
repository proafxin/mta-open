import polars as pl
import streamlit as st

from common import options

st.title("Crash map by time.")

data_load_state = st.text("Loading data...")
clean_data = pl.read_parquet("data/clean_map.parquet")
data_load_state.text("Loading data...done!")


option = st.selectbox(label="Time to filter by", options=options)


st.subheader(f"Map by {option}")
minimum = int(clean_data[option].min())  # type: ignore [arg-type]
maximum = int(clean_data[option].max())  # type: ignore [arg-type]
start_time, end_time = st.slider(option.upper(), minimum, maximum, (minimum, int(clean_data[option].median())))  # type: ignore [arg-type]
map_state = st.subheader(f"Loading crashes at {option} from {start_time} to {end_time}...")
filtered_data = clean_data.filter(pl.col(option).le(end_time))
filtered_data = filtered_data.filter(pl.col(option).ge(start_time))

st.map(filtered_data.select(["latitude", "longitude"]))

map_state.subheader(f"Loaded crashes at {option} from {start_time} to {end_time}!")
