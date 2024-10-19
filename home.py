import json

import altair
import polars as pl
import streamlit as st

st.set_page_config(page_title="NY Motor Vehicles Crash", layout="wide")
st.title("12 Years of New York Motor Vehicles Crash: Insights and Visualizations")

""
st.header("Dashboards and Overall Metrics")


with open("data/metrics.json", mode="r") as f:
    metric = json.load(f)

url = "https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data"


altair.themes.enable("dark")


col = st.columns((0.7, 1.5, 1), gap="small")


def write_metric(label: str):
    st.metric(label=label, value=metric[label])


with st.sidebar:
    st.link_button("About Dataset", url=url)
    st.subheader("Data Cleaning policy")
    text = "There are many data points that are not properly labeled. Here are the policies used to clean this data."
    st.markdown(text)
    st.markdown(
        "* Null values are not considered e.g. if location is not present, the row is not considered for map plotting."
    )
    st.markdown(
        "* Obviously, context matters. Not all columns are considered for null filtering. Street names and contributing factors can often be left empty."
    )
    st.markdown(
        "* Locations are sometimes inaccurate. For example, there are coordinates with (0,0) values. These are considered **invalid**."
    )
    st.markdown(
        "* 3 locations had distances more than 5 times the average and showed up outside the map. They were also considered invalid."
    )
    st.markdown("* Incorrectly labeled locations e.g. a crash occuring in Queens labeled as Bronx weren't discarded.")


@st.cache_resource
def load_metric(column: str) -> pl.DataFrame:
    return pl.read_parquet(f"data/{column}.parquet")


by = ["borough", "year"]


@st.cache_resource
def calculate_metrics() -> tuple[dict, dict]:
    metrics: dict[str | int, dict] = {}
    averages: dict[str, dict[str, int | float]] = {}
    for column in by:
        data = load_metric(column=column)

        averages[column] = {}
        for status in data.columns[1:]:
            averages[column][status] = int(data[status].sum()) / data[column].shape[0]

        for row in data.to_dicts():
            key = row.pop(column)
            metrics[key] = row

    return metrics, averages  # type: ignore


metrics, averages = calculate_metrics()

boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
years = range(2012, 2025)

OPTIONS = {"borough": boroughs, "year": years}


with st.container():
    with col[0]:
        subcols = st.columns((1, 1), gap="small")
        with subcols[0]:
            write_metric("Total number of crashes")
            write_metric("Crashes with time and location")
            write_metric("Total killed")
            write_metric("Total injured")

        with subcols[1]:
            write_metric("Locations marked")
            write_metric("Locations unmarked")

            write_metric("Valid markings")
            write_metric("Invalid markings")

    with col[1]:
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
