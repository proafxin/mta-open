import polars as pl
import streamlit as st

st.set_page_config(layout="wide")


st.subheader("10 Random Data Points for Different Scenarios")


@st.cache_resource
def random_data() -> pl.DataFrame:
    return pl.read_parquet("data/random.parquet")


@st.cache_resource
def invalid_data() -> pl.DataFrame:
    return pl.read_parquet("data/invalid_coordinate.parquet")


@st.cache_resource
def valid_data() -> pl.DataFrame:
    return pl.read_parquet("data/clean_map.parquet")


with st.expander("Raw Data"):
    data = random_data()
    st.dataframe(data.sample(n=10))


""
""
columns = st.columns((0.7, 0.4, 0.3), gap="small")

with columns[0]:
    with st.expander("Invalid Location Data"):
        invalid = invalid_data()
        st.dataframe(
            data=invalid.sample(n=10).select(
                ["borough", "zip_code", "latitude", "longitude", "on_street_name", "off_street_name", "date", "time"]
            )
        )

with columns[1]:
    with st.expander("Valid Location Data"):
        valid = valid_data()
        st.dataframe(data=valid.sample(n=10).select(["borough", "latitude", "longitude", "date"]))
