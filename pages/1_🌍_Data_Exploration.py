import streamlit as st
from polars import read_parquet

st.set_page_config(layout="wide")


st.subheader("10 Random Data Points for Different Scenarios")


with st.expander("Raw Data"):
    data = read_parquet("data/random.parquet")
    st.dataframe(data.sample(n=10))


""
""
columns = st.columns((0.7, 0.4, 0.3), gap="small")

with columns[0]:
    with st.expander("Invalid Location Data"):
        invalid = read_parquet("data/invalid_coordinate.parquet")
        st.dataframe(
            data=invalid.sample(n=10).select(
                ["borough", "zip_code", "latitude", "longitude", "on_street_name", "off_street_name", "date", "time"]
            )
        )

with columns[1]:
    with st.expander("Valid Location Data"):
        valid = read_parquet("data/clean_map.parquet")
        st.dataframe(data=valid.sample(n=10).select(["borough", "latitude", "longitude", "date"]))
