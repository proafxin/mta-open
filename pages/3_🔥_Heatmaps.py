from datetime import date

import folium
import folium.map
import polars as pl
import streamlit as st
from streamlit_folium import st_folium

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

ALL_COLORS = [
    "gray",
    "lightgray",
    "cadetblue",
    "lightred",
    "darkpurple",
    "purple",
    "beige",
    "orange",
    "blue",
    "darkgreen",
    "darkred",
    "darkblue",
    "black",
    "pink",
    "white",
    "lightblue",
    "lightgreen",
    "red",
    "green",
]
boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]

COLORS = ["darkred", "darkpurple", "blue", "darkblue", "purple"]
# np.random.seed = 10
# COLORS = np.random.choice(ALL_COLORS, size=len(boroughs))

color_map = {borough: color for borough, color in zip(boroughs, COLORS)}


option = "date"
minimum = date(day=1, month=7, year=2012)
maximum = date(day=8, month=10, year=2024)
median = date(day=1, month=7, year=2014)

with st.sidebar:
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
    map_data = pl.DataFrame(map_data)
    if map_data.shape[0] == 0:
        st.info(f"No data found for {selected_boroughs} on {time}")
    else:
        center = (map_data["latitude"].mean(), map_data["longitude"].mean())
        fl_map = folium.Map(location=center, tiles="cartodbpositron", zoom_start=10)

        for row in map_data.to_dicts():
            folium.Marker(
                location=row["coordinate"],
                popup=folium.Popup(html=row["borough"], parse_html=True),
                tooltip=f"({row["latitude"]}, {row["longitude"]})",
                icon=folium.Icon(color=color_map[row["borough"]], icon="angle"),
            ).add_to(fl_map)
        # HeatMapWithTime(data=map_data.drop("coordinate", "date", "borough")).add_to(fl_map)

        st_folium(fig=fl_map, use_container_width=True)

        # leaf = lm.Map(center=center)
        # st.write(map_data.head())

        # leaf.add_heatmap(data=map_data, latitude="latitude", longitude="longitude")
        # leaf.to_streamlit()


map_state.text(f"Loading map of crashes by {option} = {time}...DONE!")  # type: ignore [str-bytes-safe]
