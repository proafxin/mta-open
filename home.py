import json

import altair
import pandas as pd
import plotly.express as px
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
    templates = ["plotly", "ggplot2", "seaborn", "simple_white", "none"]
    choose_template = st.checkbox("Choose template?")
    template = None
    if choose_template:
        template = st.selectbox(label="Template", options=templates)
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
def calculate_metrics() -> tuple[dict, dict, dict[str, pd.DataFrame], dict[str, pl.DataFrame]]:
    metrics: dict[str | int, dict] = {}
    total: dict[str, dict[str, int | float]] = {}
    correlations: dict[str, pl.DataFrame] = {}
    cumulatives: dict[str, pl.DataFrame] = {}
    for column in by:
        data = load_metric(column=column)

        cumulatives[column] = data.select(
            pl.col(column),
            pl.col("number_of_persons_killed").cum_sum(),
            pl.col("number_of_persons_injured"),
            pl.col("count").cum_sum(),
        )
        df_pandas = data.drop([column, "total_damage"]).to_pandas()
        df_pandas.columns = [col.split("_")[-1].capitalize() for col in df_pandas.columns]  # type: ignore
        correlations[column] = df_pandas.corr()  # type: ignore [assignment]
        total[column] = {}
        for status in data.columns[1:]:
            total[column][status] = int(data[status].sum()) / data[column].shape[0]

        for row in data.to_dicts():
            key = row.pop(column)
            metrics[key] = row

    return metrics, total, correlations, cumulatives  # type: ignore


metrics, averages, correlations, cumulatives = calculate_metrics()

boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
years = range(2012, 2025)

OPTIONS = {"borough": boroughs, "year": years}


def draw_correlation(column: str) -> None:
    st.subheader(f"Correlation between incidents by {column}")
    corr = correlations[column]
    fig = px.imshow(corr, text_auto=True, aspect="auto", template=template)
    st.plotly_chart(fig, theme="streamlit")


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
            with subcols[-1]:
                st.download_button(
                    label=f"Correlation data for {column}s",
                    data=correlations[column].to_csv(),
                    mime="text/csv",
                    file_name=f"correlation_{column}.csv",
                )

    with col[2]:
        draw_correlation(column="borough")


with st.container():
    st.subheader("Crashes and damage over the years")
    columns = ["number_of_persons_killed", "number_of_persons_injured", "count"]
    chart = px.line(cumulatives["year"], x="year", y=columns, template=template)
    chart2 = px.line(cumulatives["borough"], x="borough", y=columns, template=template)
    st.plotly_chart(chart)
    st.subheader("Crashes and damage by boroughs")
    st.plotly_chart(chart2)
