import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

from common import options  # noqa: E402

st.title("Crash map by time.")

data_load_state = st.text("Loading data...")
clean_data = pl.read_parquet("data/clean_map.parquet")
data_load_state.text("Loading data...done!")


option = st.selectbox(label="Time to filter by", options=options)


st.subheader(f"Map by {option}")
minimum = clean_data[option].min()  # type: ignore [arg-type]
maximum = clean_data[option].max()  # type: ignore [arg-type]
value = (minimum, maximum)

start_time, end_time = st.slider(option.upper(), minimum, maximum, value)  # type: ignore [arg-type, type-var]
boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
selected_boroughs = options = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs)

map_state = st.text(f"Loading map of crashes by {option} from {start_time} to {end_time}...")  # type: ignore [str-bytes-safe]
filtered_data = clean_data.filter(pl.col("borough").is_in(selected_boroughs))
filtered_data = filtered_data.filter(pl.col(option).le(end_time))
filtered_data = filtered_data.filter(pl.col(option).ge(start_time))

st.map(filtered_data.select(["latitude", "longitude"]))
