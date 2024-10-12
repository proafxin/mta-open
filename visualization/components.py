import duckdb
import streamlit as st
from polars import DataFrame, read_parquet

from cleaner import sanitize
from workflow.assets.constants import DUCKDB_LOCATION


@st.cache_data
def execute(query: str) -> DataFrame:
    with duckdb.connect(DUCKDB_LOCATION) as conn:
        return conn.execute(query=query).pl()


@st.cache_data
def vehicles_crash_data() -> DataFrame:
    # data = execute(query="select * from 'vehicle_crash'")
    # data = read_csv(
    #     "https://drive.usercontent.google.com/download?id=1cHOFJE6uZEjfsHUd3Q67xiyTCuCMPVhF&export=download&authuser=0&confirm=t&uuid=323fb3c5-7397-4e6d-a379-ea08496d1a5b&at=AN_67v2pE0AGSnWeASB8TBCTAaMT:1728737337209"
    # )
    data = read_parquet(
        "https://drive.usercontent.google.com/download?id=1rqxFIcm8NhTnkgNd9Pc5aCojLl7U9qp7&export=download&authuser=0&confirm=t&uuid=74aff7db-a9d8-4b55-be87-222682b88099&at=AN_67v1Q_flVVQMjtwASDrwuzVU5:1728739314404"
    )
    data.columns = [sanitize(column, lower=True) for column in data.columns]

    return data


event_type = "Event_Type"
