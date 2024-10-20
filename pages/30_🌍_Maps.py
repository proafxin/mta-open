from datetime import date
from enum import Enum

import folium
import folium.map
import geopandas as gpd
import pandas as pd
import polars as pl
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(layout="wide")


def form_mapfilename(col: str) -> str:
    col = col.lower().strip().replace(" ", "_")
    filename = f"data/maps/{col}.parquet"

    return filename


COLOUR_RANGE = [[217, 20, 122, 200], [235, 100, 33, 200], [14, 166, 204, 200], [131, 28, 161, 200], [100, 10, 225, 220]]
COLORS_CODE = ["#0044ff", "#ffaa00", "#00ff00", "#ff7f0e", "#2ca02c"]

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
BOROUGH_CODES = {borough: code for borough, code in zip(boroughs, [2, 4, 3, 1, 5])}

COLORS = ["darkred", "darkpurple", "blue", "darkblue", "purple"]
# np.random.seed = 10
# COLORS = np.random.choice(ALL_COLORS, size=len(boroughs))

color_map = {borough: color for borough, color in zip(boroughs, COLORS)}


option = "date"
minimum = date(day=1, month=7, year=2012)
maximum = date(day=8, month=10, year=2024)
median = date(day=1, month=7, year=2014)

columns = ["number_of_crash", "number_of_persons_killed", "number_of_persons_injured", "number_of_casualty"]
columns_readable = [col.capitalize().replace("_", " ") for col in columns]
COLUMN_MAP = {col1: col2 for col1, col2 in zip(columns_readable, columns)}


class MapType(str, Enum):
    HEATMAP = "Heatmap"
    GEOGRAPHICAL = "Geographical Map"
    BAR = "Bar chart of incidents"


@st.cache_resource
def load_multiple_borough_maps(selected_boroughs: list[str]) -> tuple[pl.DataFrame, dict[str, int]]:
    if len(selected_boroughs) == 0:
        return pl.DataFrame(), {}

    data = []
    value_counts: dict[str, int] = {}
    for col in selected_boroughs:
        filtered_data = pl.read_parquet(form_mapfilename(col=col))
        filtered_data = filtered_data.filter(pl.col(option).eq(time))
        value_counts[col] = filtered_data.shape[0]

        data.append(filtered_data)
    map_data = pl.concat(data)
    map_data = pl.DataFrame(map_data)

    return map_data, value_counts


@st.cache_resource
def load_geo_data() -> gpd.GeoDataFrame:
    return gpd.read_parquet("data/nyc_projected.parquet")


@st.cache_resource
def load_borough_data() -> pd.DataFrame:
    data = pd.read_parquet("data/borough.parquet")
    data["code"] = data["borough"].apply(lambda x: BOROUGH_CODES[x.upper()])
    data = data.drop("borough", axis=1)

    return data


with st.sidebar:
    map_type = st.selectbox(label="Choose type", options=[MapType.GEOGRAPHICAL.value, MapType.HEATMAP.value])


if map_type == MapType.GEOGRAPHICAL:
    with st.sidebar:
        time = st.slider(label=f"Pick a {option}", min_value=minimum, max_value=maximum, value=median)
        selected_boroughs = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs[:])

    map_data, value_counts = load_multiple_borough_maps(selected_boroughs=selected_boroughs)

    if map_data.shape[0] == 0:
        st.info(f"No data found for {selected_boroughs} on {time}")
    else:
        map_data = map_data.with_columns(pl.col("borough").str.replace_many(boroughs, COLORS).alias("color"))

        borough_counts = map_data["borough"].value_counts()

        center = (map_data["latitude"].mean(), map_data["longitude"].mean())
        fl_map = folium.Map(location=center, tiles=None, zoom_start=15)
        folium.TileLayer(tiles="OpenStreetMap").add_to(fl_map)

        for row in map_data.to_dicts():
            tooltip = f"Location: ({row["latitude"]}, {row["longitude"]})"
            for col in columns[1:]:
                tooltip += f", {col.replace("_", " ").capitalize()}: {row[col]}"
            folium.Marker(
                location=row["coordinate"],
                popup=f"{value_counts[row['borough']]} crashes in {row["borough"]}",
                tooltip=tooltip,
                icon=folium.Icon(color=color_map[row["borough"]], icon="angle"),
            ).add_to(fl_map)
        sw = list(map_data.select("latitude", "longitude").min().to_numpy()[0])
        ne = list(map_data.select("latitude", "longitude").max().to_numpy()[0])
        fl_map.fit_bounds([sw, ne])

        st_folium(fig=fl_map, use_container_width=True, returned_objects=[])
elif map_type == MapType.HEATMAP.value:
    selected_column = st.selectbox("Generate heatmap for", COLUMN_MAP.keys())
    column = COLUMN_MAP[selected_column]

    geo_data = load_geo_data()
    borough_data = load_borough_data()
    # geo_data["color"] = geo_data["borough"].apply(lambda x: color_map[x.upper()])

    fl_map = folium.Map(location=(40.71261963846181, -73.95064260553615), zoom_start=10.4, tiles=None)
    folium.TileLayer("CartoDB positron", name="Light Map", control=False).add_to(fl_map)
    myscale = (borough_data[column].quantile((0, 0.1, 0.75, 0.9, 0.98, 1))).tolist()  # type: ignore

    folium.Choropleth(
        geo_data=geo_data,
        data=borough_data,
        columns=["code", column],
        key_on="feature.properties.code",
        # fill_color="YlGnBu",
        legend_name=f"{column.replace("_", " ").capitalize()}",
        fill_opacity=1,
        line_opacity=0.2,
    ).add_to(fl_map)

    folium.LayerControl().add_to(fl_map)
    st_folium(fl_map, use_container_width=True, returned_objects=[])
