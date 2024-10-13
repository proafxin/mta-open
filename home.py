import streamlit as st
from polars import read_parquet

from cleaner import sanitize

st.set_page_config(layout="wide")
st.title("Interact and Visualize Vehicle Crash Data by MTA Open")
st.write("# Initial Analysis")


data_load_state = st.text("Loading data...")
with open("data/vehicle_crash.parquet", mode="rb") as f:
    st.session_state["contents"] = f.read()

data = read_parquet(st.session_state["contents"])
data.columns = [sanitize(column, lower=True) for column in data.columns]
data_load_state.text("Loading data...done!")

if st.checkbox("Show raw data"):
    st.subheader("Sample data")
    st.dataframe(data.head())

st.write(f"#### Total data points: {data.shape[0]}")
st.write(f"#### Number of variables: {data.shape[1]}")

st.subheader("Count by variables")
count_columns = data.columns[2:3] + data.columns[7:-6] + data.columns[-5:]
column = st.selectbox("Select a variable", count_columns)
count_load_state = st.text(f"Count by {column}...")
st.dataframe(data[column].value_counts())
count_load_state.text(f"Count by `{column}` loaded.")
