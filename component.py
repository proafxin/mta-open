import re

import streamlit as st
from polars import DataFrame, read_parquet


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
