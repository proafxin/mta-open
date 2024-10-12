import re

import streamlit as st
from polars import DataFrame, read_parquet

st.set_page_config(layout="wide")
st.title("Interact and Visualize Vehicle Crash Data by MTA Open")


def sanitize(text: str, lower: bool = False) -> str:
    if lower:
        text = text.lower()

    text = re.sub(r"[-. ]", "_", text)
    pattern = r"[^a-zA-Z0-9_]"

    return re.sub(pattern=pattern, string=text, repl="")


@st.cache_resource
def vehicles_crash_data() -> DataFrame:
    data = read_parquet("data/vehicle_crash.parquet")
    data.columns = [sanitize(column, lower=True) for column in data.columns]

    return data


st.write("# Initial Analysis")
data_load_state = st.text("Downloading data...")
data = vehicles_crash_data()
data_load_state.text("Downloading data...done!")

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
