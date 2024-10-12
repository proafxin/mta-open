import duckdb
import streamlit as st
from polars import DataFrame

from workflow.assets.constants import DUCKDB_LOCATION


@st.cache_data
def execute(query: str) -> DataFrame:
    with duckdb.connect(DUCKDB_LOCATION) as conn:
        return conn.execute(query=query).pl()


vehicles_data = execute(query="select * from 'vehicle_crash'")
