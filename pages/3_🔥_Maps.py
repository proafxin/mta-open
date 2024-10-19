from datetime import date
from enum import Enum

import folium
import folium.map
import geopandas as gpd
import plotly.express as px
import polars as pl
import streamlit as st
from plotly.io import templates
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

COLORS = ["darkred", "darkpurple", "blue", "darkblue", "purple"]
# np.random.seed = 10
# COLORS = np.random.choice(ALL_COLORS, size=len(boroughs))

color_map = {borough: color for borough, color in zip(boroughs, COLORS)}


option = "date"
minimum = date(day=1, month=7, year=2012)
maximum = date(day=8, month=10, year=2024)
median = date(day=1, month=7, year=2014)

columns = ["number_of_persons_killed", "number_of_persons_injured", "count", "number_of_casualty"]
columns_readable = [col.capitalize().replace("_", " ") for col in columns]
COLUMN_MAP = {col1: col2 for col1, col2 in zip(columns_readable, columns)}


class MapType(str, Enum):
    HEATMAP = "Heatmap"
    GEOGRAPHICAL = "Geographical Map"
    BAR = "Bar chart of incidents"


@st.cache_resource
def load_multiple_borough_maps(selected_boroughs: list[str]) -> pl.DataFrame:
    data = []
    for col in selected_boroughs:
        filtered_data = pl.read_parquet(form_mapfilename(col=col))
        filtered_data = filtered_data.filter(pl.col(option).eq(time))

        data.append(filtered_data)
    map_data = pl.concat(data)
    map_data = pl.DataFrame(map_data)

    return map_data


@st.cache_resource
def load_geo_data() -> gpd.GeoDataFrame:
    return gpd.read_parquet("data/heatmap.parquet")


with st.sidebar:
    map_type = st.selectbox(label="Choose type", options=[MapType.GEOGRAPHICAL.value, MapType.HEATMAP.value])


if map_type == MapType.GEOGRAPHICAL:
    with st.sidebar:
        time = st.slider(label=f"Pick a {option}", min_value=minimum, max_value=maximum, value=median)
        selected_boroughs = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs[:])

    map_data = load_multiple_borough_maps(selected_boroughs=selected_boroughs)
    map_data = map_data.with_columns(pl.col("borough").str.replace_many(boroughs, COLORS).alias("color"))
    if map_data.shape[0] == 0:
        st.info(f"No data found for {selected_boroughs} on {time}")
    else:
        center = (map_data["latitude"].mean(), map_data["longitude"].mean())
        fl_map = folium.Map(location=center, tiles="cartodbpositron", zoom_start=10)
        folium.TileLayer(tiles="OpenStreetMap").add_to(fl_map)

        for row in map_data.to_dicts():
            folium.Marker(
                location=row["coordinate"],
                popup=row["borough"],
                tooltip=f"Location: ({row["latitude"]}, {row["longitude"]})",
                icon=folium.Icon(color=color_map[row["borough"]], icon="angle"),
            ).add_to(fl_map)
        sw = list(map_data.select("latitude", "longitude").min().to_numpy()[0])
        ne = list(map_data.select("latitude", "longitude").max().to_numpy()[0])
        fl_map.fit_bounds([sw, ne])

        st_folium(fig=fl_map, use_container_width=True, returned_objects=[])
elif map_type == MapType.HEATMAP.value:
    selected_column = st.selectbox("Generate heatmap for", COLUMN_MAP.keys())
    column = COLUMN_MAP[selected_column]
    template = None
    color_scale = None

    with st.sidebar:
        choose_template = st.checkbox("Choose template?")
        if choose_template:
            template = st.selectbox(label="Template", options=templates)

        choose_color_scale = st.checkbox("Choose color scale?")
        if choose_color_scale:
            color_scale = st.selectbox(label="Color scale", options=px.colors.named_colorscales())  # type:  ignore

    geo_data = load_geo_data()
    hover_names = [col.replace("_", " ").capitalize() for col in geo_data.columns]

    geo_data = geo_data.set_index("borough")
    fig = px.choropleth(
        geo_data,
        geojson=geo_data.geometry,
        locations=geo_data.index,
        color=column,
        template=template,
        color_continuous_scale=color_scale,
        height=950,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    st.plotly_chart(fig)
