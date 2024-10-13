import plotly.express as px
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

st.write(f"Total data points: {data.shape[0]}, number of variables: {data.shape[1]}")

st.subheader("Select a variable and see number of crashes for different values.")
count_columns = data.columns[2:3] + data.columns[7:-6] + data.columns[-5:]
column = st.selectbox("Variable", count_columns)
value_counts = data[column].drop_nulls().value_counts(sort=True)
top = st.slider(
    "How many do you want to show?",
    min_value=1,
    max_value=int(min(20, value_counts.shape[0])),
)
count_load_state = st.text(f"Count by {column}...")
value_counts = value_counts.head(n=top)

fig = px.pie(
    value_counts,
    values="count",
    names=column,
    title=f"Number of crashes for top {top} values of {column}",
)
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
count_load_state.text(f"Count by `{column}` loaded.")

del data
