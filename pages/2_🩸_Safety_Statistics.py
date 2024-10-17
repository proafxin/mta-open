import polars as pl
import streamlit as st

st.set_page_config(layout="wide")


st.header("Safety Statistics")
safety_columns = ["year", "month", "hour"]

status_readable_names = {
    "number_of_persons_killed": "death",
    "number_of_persons_injured": "injury",
    "total_damaged": "total damage",
}


safety_cols = st.columns((1,) * len(safety_columns), gap="small")

for i, column in enumerate(safety_columns):
    with safety_cols[i]:
        with st.expander("Click to see stats"):
            pivot = pl.read_parquet(f"data/borough_{column}.parquet")
            st.dataframe(pivot)
