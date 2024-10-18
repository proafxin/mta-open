from datetime import date

import polars as pl
import streamlit as st

st.set_page_config(layout="wide")


st.title("Map of crashes by date")


def form_mapfilename(col: str) -> str:
    col = col.lower().strip().replace(" ", "_")
    filename = f"data/maps/{col}.parquet"

    return filename


@st.cache_resource
def load_map_data(col: str) -> pl.DataFrame:
    return pl.read_parquet(form_mapfilename(col=col))


COLOUR_RANGE = [[217, 20, 122, 200], [235, 100, 33, 200], [14, 166, 204, 200], [131, 28, 161, 200], [100, 10, 225, 220]]
COLORS = ["#0044ff", "#ffaa00", "#00ff00", "#ff7f0e", "#2ca02c"]

boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
color_map = {borough: color for borough, color in zip(boroughs, COLORS)}


option = "date"
minimum = date(day=1, month=7, year=2012)
maximum = date(day=8, month=10, year=2024)
median = date(day=1, month=7, year=2014)


time = st.slider(label=f"Pick a {option}", min_value=minimum, max_value=maximum, value=median)
selected_boroughs = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs[:])
map_state = st.text(f"Loading map of crashes by {option} = {time}...")  # type: ignore [str-bytes-safe]

data = []
for col in selected_boroughs:
    filtered_data = load_map_data(col=col)
    filtered_data = filtered_data.filter(pl.col(option).eq(time))
    filtered_data = filtered_data.with_columns(pl.col("borough").str.replace_many(boroughs, COLORS).alias("color"))
    data.append(filtered_data)


with st.container():
    map_data = pl.concat(data)
    if map_data.shape[0] == 0:
        st.info(f"No data found for {selected_boroughs} on {time}")
    else:
        st.map(data=map_data, latitude="latitude", longitude="longitude", color="color", height=750)


map_state.text(f"Loading map of crashes by {option} = {time}...DONE!")  # type: ignore [str-bytes-safe]
