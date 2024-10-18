from datetime import date

import polars as pl
import streamlit as st

st.set_page_config(layout="wide")


st.title("Map of incidents")


@st.cache_resource
def load_data() -> pl.DataFrame:
    return pl.read_parquet("data/clean_map.parquet")


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


clean_data = load_data()

data_load_state = st.text("Loading data...")
data_load_state.text("Loading data...done!")


option = "date"
st.subheader(f"{option.capitalize()} range")
minimum = date(day=1, month=7, year=2012)
maximum = date(day=8, month=10, year=2024)
median = date(day=1, month=7, year=2014)

value = (clean_data[option].dt.min(), median)


start_time, end_time = st.slider(option.upper(), minimum, maximum, value)  # type: ignore [arg-type, type-var]
selected_boroughs = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs[:])
map_state = st.text(f"Loading map of crashes by {option} from {start_time} to {end_time}...")  # type: ignore [str-bytes-safe]

data = []
for col in selected_boroughs:
    filtered_data = load_map_data(col=col)
    filtered_data = filtered_data.filter(pl.col(option).le(end_time))
    filtered_data = filtered_data.filter(pl.col(option).ge(start_time))
    filtered_data = filtered_data.with_columns(pl.col("borough").str.replace_many(boroughs, COLORS).alias("color"))
    data.append(filtered_data)

with st.container():
    st.map(data=pl.concat(data), latitude="latitude", longitude="longitude", color="color", height=750)

# st.map(data=filtered_data, latitude="latitude", longitude="longitude", color="color", height=750)
map_state.text(f"Loading map of crashes by {option} from {start_time} to {end_time}...DONE!")  # type: ignore [str-bytes-safe]


# chart_data = pd.DataFrame(
#     filtered_data.select(["latitude", "longitude", "borough"]).to_numpy(), columns=["lat", "lon", "borough"]
# )

# calculate colour range mapping index to then assign fill colour
# chart_data["color"] = chart_data["borough"].map(lambda x: color_map[x])


# view_state = pydeck.ViewState(
#     latitude=filtered_data["latitude"].mean(), longitude=filtered_data["longitude"].mean(), zoom=9.5
# )

# layer = pydeck.Layer(
#     "ScatterplotLayer", data=chart_data, get_position="[lon, lat]", get_color="color", pickable=True, get_radius=100
# )

# deck = pydeck.Deck(initial_view_state=view_state, layers=[layer], map_provider="mapbox")
# st.pydeck_chart(deck)
