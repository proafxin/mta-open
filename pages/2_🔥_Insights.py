import json

import polars as pl
import streamlit as st

with open("data/metrics.json", mode="r") as f:
    metric = json.load(f)

col = st.columns((0.45, 1, 0.67), gap="small")


def write_metric(label: str):
    st.metric(label=label, value=metric[label])


@st.cache_resource
def load_metric(column: str) -> pl.DataFrame:
    return pl.read_parquet(f"data/{column}.parquet")


by = ["borough", "year"]


@st.cache_resource
def calculate_metrics() -> tuple[dict, dict, dict, dict]:
    metrics: dict[str | int, dict] = {}
    averages: dict[str, dict[str, int | float]] = {}
    minimums: dict[str, dict[str, tuple[str | int, int]]] = {}
    maximums: dict[str, dict[str, tuple[str | int, int]]] = {}

    for column in by:
        data = load_metric(column=column)

        averages[column] = {}
        minimums[column] = {}
        maximums[column] = {}

        for status in data.columns[1:]:
            averages[column][status] = int(data[status].sum()) / data[column].shape[0]
            sorted_data = data.select(column, status).sort(by=status)
            min_row = sorted_data.row(0)
            max_row = sorted_data.row(-1)
            minimums[column][status] = min_row
            maximums[column][status] = max_row

        for row in data.to_dicts():
            key = row.pop(column)
            metrics[key] = row

    return metrics, averages, minimums, maximums  # type: ignore


metrics, averages, minimums, maximums = calculate_metrics()

boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
years = range(2012, 2025)

OPTIONS = {"borough": boroughs, "year": years}


def min_max_metric(column: str, status: str) -> None:
    value = minimums[column][status][0]
    if isinstance(value, str):
        value = " ".join([token.lower().capitalize() for token in value.split(" ")])
    st.metric(label=f"{column.capitalize()} with least {status.replace("_", " ")}", value=value)


with st.container():
    with col[0]:
        subcols = st.columns((1, 1), gap="small")
        with subcols[0]:
            write_metric("Total number of crashes")
            write_metric("Crashes with time, location")
            write_metric("Total killed")
            write_metric("Total injured")

        with subcols[1]:
            write_metric("Locations marked")
            write_metric("Locations unmarked")

            write_metric("Valid markings")
            write_metric("Invalid markings")

    with col[1]:
        with st.expander("Reveal the riskiest borough"):
            st.text("Manhattan")
        for column in by:
            selected = st.selectbox(label=f"By {column}", options=OPTIONS[column])
            keys = list(averages["borough"].keys())
            subcols = st.columns((1,) * (len(keys) + 1), gap="small")

            for i, key in enumerate(keys):
                with subcols[i]:
                    value = metrics[selected][key]
                    delta = value - averages[column][key]
                    delta = round(delta, 2)
                    st.metric(
                        label=" ".join(str(key).capitalize().split("_")),
                        value=value,
                        delta=delta,
                        delta_color="inverse",
                    )

    with col[2]:
        with st.expander("Reveal the safest borough"):
            st.text("Staten Island")
        subcols = st.columns((1,) * len(by))

        for i, column in enumerate(by):
            with subcols[i]:
                for status in minimums[column]:
                    min_max_metric(column=column, status=status)
