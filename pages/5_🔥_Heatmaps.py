from datetime import date

import polars as pl
import streamlit as st

st.set_page_config(layout="wide")


st.title("Map of incidents")


@st.cache_resource
def load_data() -> pl.DataFrame:
    return pl.read_parquet("data/clean_map.parquet")


clean_data = load_data()

data_load_state = st.text("Loading data...")
data_load_state.text("Loading data...done!")


option = "date"
st.subheader(f"{option.capitalize()} range")
minimum = clean_data[option].min()  # type: ignore [arg-type]
maximum = clean_data[option].max()  # type: ignore [arg-type]
median = clean_data[option].median()
if option == "date":
    median = date(day=median.day, month=median.month, year=median.year)  # type: ignore [union-attr]
else:
    median = int(median)  # type: ignore [arg-type]
value = (clean_data[option].dt.min(), median)


start_time, end_time = st.slider(option.upper(), minimum, maximum, value)  # type: ignore [arg-type, type-var]
boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
selected_boroughs = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs[:])

filtered_data = clean_data.filter(pl.col("borough").is_in(selected_boroughs))
filtered_data = filtered_data.filter(pl.col(option).le(end_time))
filtered_data = filtered_data.filter(pl.col(option).ge(start_time))


# chart_data = pd.DataFrame(
#     filtered_data.select(["latitude", "longitude", "borough"]).to_numpy(), columns=["lat", "lon", "borough"]
# )

COLOUR_RANGE = [[217, 20, 122, 200], [235, 100, 33, 200], [14, 166, 204, 200], [131, 28, 161, 200], [100, 10, 225, 220]]

COLORS = ["#0044ff", "#ffaa00", "#00ff00", "#ff7f0e", "#2ca02c"]

color_map = {borough: color for borough, color in zip(boroughs, COLORS)}
# calculate colour range mapping index to then assign fill colour
# chart_data["color"] = chart_data["borough"].map(lambda x: color_map[x])

filtered_data = filtered_data.with_columns(pl.col("borough").str.replace_many(boroughs, COLORS).alias("color"))

map_state = st.text(f"Loading map of crashes by {option} from {start_time} to {end_time}...")  # type: ignore [str-bytes-safe]

st.map(data=filtered_data, latitude="latitude", longitude="longitude", color="color", height=750)

# view_state = pydeck.ViewState(
#     latitude=filtered_data["latitude"].mean(), longitude=filtered_data["longitude"].mean(), zoom=9.5
# )

# layer = pydeck.Layer(
#     "ScatterplotLayer", data=chart_data, get_position="[lon, lat]", get_color="color", pickable=True, get_radius=100
# )

# deck = pydeck.Deck(initial_view_state=view_state, layers=[layer], map_provider="mapbox")
# st.pydeck_chart(deck)

map_state.text(f"Loading map of crashes by {option} from {start_time} to {end_time}...DONE!")  # type: ignore [str-bytes-safe]
