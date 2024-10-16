from datetime import date

import pandas as pd
import polars as pl
import pydeck
import streamlit as st

st.set_page_config(layout="wide")

from common import options  # noqa: E402

st.title("Map of incidents")


data_load_state = st.text("Loading data...")
clean_data = pl.read_parquet("data/clean_map.parquet")
data_load_state.text("Loading data...done!")


option = st.selectbox(label="Time to filter by", options=options)


st.subheader(f"Map by {option}")
minimum = clean_data[option].min()  # type: ignore [arg-type]
maximum = clean_data[option].max()  # type: ignore [arg-type]
median = clean_data[option].median()
if option == "date":
    median = date(day=median.day, month=median.month, year=median.year)  # type: ignore [union-attr]
else:
    median = int(median)  # type: ignore [arg-type]
value = (clean_data[option].dt.min(), median)

st.write(clean_data[option].dt.min(), clean_data[option].dt.max(), value)


start_time, end_time = st.slider(option.upper(), minimum, maximum, value)  # type: ignore [arg-type, type-var]
boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
selected_boroughs = options = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs[:2])

map_state = st.text(f"Loading map of crashes by {option} from {start_time} to {end_time}...")  # type: ignore [str-bytes-safe]
filtered_data = clean_data.filter(pl.col("borough").is_in(selected_boroughs))
filtered_data = filtered_data.filter(pl.col(option).le(end_time))
filtered_data = filtered_data.filter(pl.col(option).ge(start_time))


chart_data = pd.DataFrame(
    filtered_data.select(["latitude", "longitude", "borough"]).to_numpy(), columns=["lat", "lon", "borough"]
)

COLOUR_RANGE = [[217, 20, 122, 200], [235, 100, 33, 200], [14, 166, 204, 200], [131, 28, 161, 200], [22, 28, 100, 200]]

boroughs = filtered_data["borough"].unique().to_list()
color_map = {borough: color for borough, color in zip(boroughs, COLOUR_RANGE)}
# calculate colour range mapping index to then assign fill colour
chart_data["color"] = chart_data["borough"].map(lambda x: color_map[x])

view_state = pydeck.ViewState(latitude=filtered_data["latitude"].mean(), longitude=filtered_data["longitude"].mean())

layer = pydeck.Layer(
    "ScatterplotLayer",
    data=chart_data,
    get_position="[lon, lat]",
    get_color="color",
    pickable=True,
    radius=200,
)

st.pydeck_chart(pydeck.Deck(initial_view_state=view_state, layers=[layer], map_provider="carto", map_style="light"))
