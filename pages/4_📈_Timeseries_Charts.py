import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

from common import MAXIMUMS, MEDIANS, MINIMUMS, options  # noqa: E402

option = st.selectbox(label="Time to filter by", options=options)


@st.cache_resource
def load_time_data(boroughs: list[str], option: str) -> pl.DataFrame:
    data = pl.read_parquet(f"data/borough__{option}.parquet")

    return data.filter(pl.col("borough").is_in(boroughs))


minimum = MINIMUMS[option]
maximum = MAXIMUMS[option]
value = (minimum, MEDIANS[option])
start_time, end_time = st.slider(option.upper(), minimum, maximum, value)  # type: ignore [call-overload]

boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]

selected_boroughs = st.multiselect("Which boroughs do you want to check?", boroughs, boroughs)

COLUMNS = {
    "Number of Crashes": "count",
    "Number of persons killed": "number_of_persons_killed",
    "Number of persons injured": "number_of_persons_injured",
}

column = st.selectbox(label="Check statistics for", options=COLUMNS.keys())

data = load_time_data(boroughs=selected_boroughs, option=option)
data = data.filter(pl.col(option).is_between(lower_bound=start_time, upper_bound=end_time))


""
st.line_chart(data=data, x=option, y=COLUMNS[column], color="borough")
""
