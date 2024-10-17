import streamlit as st
from polars import read_parquet

data = read_parquet("data/processed.parquet")

st.subheader("Sample data")
st.dataframe(data.sample(n=10))
