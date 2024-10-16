import altair
import streamlit as st
from polars import read_parquet

st.set_page_config(layout="wide")
st.title("Interactive Visualization of New York Motor Vehicles Crash Open Data")

"""
Find details about the dataset [here](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data).
"""

data_load_state = st.text("Loading data...")
data = read_parquet("data/vehicle_crash.parquet")
data_load_state.text("Loading data...done!")

if st.checkbox("Show raw data"):
    st.subheader("Sample data")
    st.dataframe(data.head())

st.subheader("Number of crashes based on factors")
count_columns = data.columns[2:3] + data.columns[10:-6]
column = st.selectbox("Variable", count_columns)
value_counts = data[column].drop_nulls().value_counts(sort=True)
chart = altair.Chart(value_counts).mark_circle().encode(x=column, y="count", size="count", color=column)
st.altair_chart(altair_chart=chart)

st.header("Number of Crashes")
st.metric("Total", data.shape[0])
marked = data["borough"].drop_nulls().shape[0]
st.metric("Marked in boroughs", marked)
st.metric("Unmarked crashes", data.shape[0] - marked)
