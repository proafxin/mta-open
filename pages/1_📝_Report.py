from enum import Enum

import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import streamlit as st
from plotly.io import templates
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")


def draw_correlation(data: pl.DataFrame, column: str | None = None, template: str | None = None) -> None:
    if column:
        st.subheader(f"Correlation between incidents by {column}")
        data = data.drop(column)
    df_pandas = data.clone().to_pandas()
    df_pandas.columns = [col.split("_")[-1].capitalize() for col in df_pandas.columns]  # type: ignore
    corr = df_pandas.corr()  # type: ignore [assignment]
    fig = px.imshow(corr, text_auto=True, aspect="auto", template=template)
    st.plotly_chart(fig, theme="streamlit")


st.title("High Level Report")
st.markdown(
    "The report in this page provides a comprehensive overall review of the crash incidents. A new acquiantance of this data should start from this page."
)

boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]
CODES = [2, 4, 3, 1, 5]
BOROUGH_CODES = {borough: code for borough, code in zip(boroughs, [2, 4, 3, 1, 5])}


@st.cache_resource
def load_processed_data() -> pl.DataFrame:
    return pl.read_parquet("data/processed.parquet")


@st.cache_resource
def load_clean_data() -> pl.DataFrame:
    data = pl.read_parquet("data/clean_data.parquet")
    data = data.with_columns(pl.col("borough").replace(BOROUGH_CODES).alias("code"))

    return data


@st.cache_resource
def load_geo_data() -> gpd.GeoDataFrame:
    return gpd.read_parquet("data/nyc_projected.parquet")


data = load_processed_data()


@st.cache_resource
def donut(cols: list[str], legendgroup: int = 1) -> go.Pie:
    donut = pl.DataFrame({col: data[col].sum() for col in cols})
    donut = donut.with_columns(pl.col(cols[0]).sub(pl.sum_horizontal(cols[1:])).alias(f"{cols[0]}_in_vehicle"))
    donut = donut.drop(cols[0])

    return go.Pie(
        labels=[col.capitalize().replace("_", " ") for col in donut.columns],
        values=donut.row(0),
        hole=0.3,
        textinfo="value+percent",
        name=cols[0].capitalize().replace("_", " "),
        text=[cols[0].capitalize().replace("_", " ")],
        legendgroup=legendgroup,
    )


@st.cache_resource
def donuts() -> go.Figure:
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]])
    pie1 = donut(
        cols=[
            "number_of_persons_injured",
            "number_of_pedestrians_injured",
            "number_of_cyclist_injured",
            "number_of_motorist_injured",
        ],
        legendgroup=1,
    )
    pie2 = donut(
        cols=[
            "number_of_persons_killed",
            "number_of_pedestrians_killed",
            "number_of_cyclist_killed",
            "number_of_motorist_killed",
        ],
        legendgroup=2,
    )
    fig.add_trace(pie1, 1, 1)
    fig.add_trace(pie2, 1, 2)
    fig.update_layout(legend_tracegroupgap=100)

    return fig


st.header("Raw Data")
st.markdown("This section displays the top 5 rows of the raw data after some processing.")
st.write(data.head())
st.write("Numer of entries in data:", data.shape[0], "Number of factors:", data.shape[1])
st.markdown("As you can see, there are some new columns in this data.")
st.markdown(
    "* `date` and `time` are the columns `crash_date` and `crash_time` with appropriate date and time types respectively."
)
st.markdown(
    "* `year`, `month`, `weekday` and `hour` columns are extracted from existing `date` and `time` columns. `weekday` starts at Monday (1) and ends in Sunday (7)."
)
st.markdown("* `number_of_casualty = number_of_persons_killed+number_of_persons_injured`")

st.header("Number of Missing Values For Each Column")
null_count = data.null_count()
columns = null_count.columns
st.write(null_count)
st.bar_chart(
    data=pl.DataFrame({"columns": columns, "null_count": null_count.transpose()}),
    x="columns",
    y="null_count",
    color="columns",
    use_container_width=True,
    height=300,
    y_label="Values missing",
)


st.header("Position of Victims")
donut_cols = st.columns((1,) * 2, gap="small")
donut_chart = donuts()
st.plotly_chart(donut_chart)
st.write(
    "As we can see, the number of victims is the lowest for people inside the vehicles consistently where motor cyclists and pedestrians fall to these accidents the most. They make up more than 90 percent of the victims on average."
)
st.write("We also see that a pedestrian is more likely to die in a crash than other people involved.")

st.header("What time of the day is the riskiest?")
hour_counts = data["hour"].value_counts().sort(by=["count"])
weekday_counts = data["weekday"].value_counts().sort(by=["count"])


hour_cols = st.columns((1,) * 2, gap="small")
with st.container():
    with hour_cols[0]:
        st.write(hour_counts)
    with hour_cols[1]:
        st.bar_chart(data=hour_counts, x="hour", y="count", height=400, color="hour", y_label="Crash count by hour")
st.write(
    "It is safe to say 1-6 AM e.g. night time are the safest to drive as these 6 hours have the lowest 6 counts of crashes. On the other hand, 4-5 PM are the riskiest with the highest counts."
)

st.header("What weekdays are the safest?")
weekday_cols = st.columns((1,) * 2, gap="small")
with weekday_cols[0]:
    st.write(weekday_counts)
with weekday_cols[1]:
    st.bar_chart(data=weekday_counts, x="weekday", y="count", color="weekday", y_label="Weekay counts")
st.write(
    "Weekends have the minimum number of crashes, specially Sunday. On the other hand, Friday sees the most number of crashes."
)

st.header("Safest Year?")
year_counts = data["year"].drop_nulls().value_counts().sort(by=["count"])
year_cols = st.columns((1,) * 2, gap="small")
with year_cols[0]:
    st.write(year_counts)
with year_cols[1]:
    st.bar_chart(data=year_counts, x="year", y="count", color="year", y_label="Crash count by year", height=400)
st.write(
    "The most number of crashes were recorded in 2016-18. It seems the number is consistently low after 2020. As of 22 October 2024, 2024 hasn't ended yet so data is incomplete for 2024."
)

st.header("Overall Borough Safety")
borough_counts = data["borough"].drop_nulls().value_counts().sort(by=["count"])
borough_cols = st.columns((1,) * 2, gap="small")
with borough_cols[0]:
    st.write(borough_counts)
with borough_cols[1]:
    st.bar_chart(data=borough_counts, x="borough", y="count", color="borough", y_label="Crash count by borough")
st.write(
    "Clearly Staten Island is the safest and Brooklyn is the riskiest, however, we should also consider area and population. Larger area means more streets and higher population means streets will be more crowded with both people and vehicles. Both factors affect the likelihood of the vehicles colliding. We will take a deeper look at this below. First we clean the data."
)

geo_data = load_geo_data()


st.header("Cleaned Data")
clean = load_clean_data()
st.write(clean.head())
st.write("Number of entries after cleaning:", clean.shape[0])
st.write(
    "We also have two new columns `distance` and `code`. `distance` is the distance between the current location and the center of New York which is supposedly `(40.71261963846181, -73.95064260553615)`. `code` is simply a mapping of boroughs to categorical integer values which is the same as in geographical data."
)
# st.write(clean.select("coordinate", "code").to_pandas().dtypes)

# merged = geo_data.merge(clean.select("coordinate", "code").to_pandas(), on="code")
# st.write(merged.head())

st.header("Correlation")


metric_cols = ["distance", "number_of_persons_killed", "number_of_persons_injured", "number_of_casualty"]


class ReportType(str, Enum):
    CHART = "Chart"
    DATAFRAME = "Display data"
    FILE_DOWNLOAD = "Download full data"


with st.sidebar:
    reporting = st.selectbox(label="Output type", options=[ReportType.CHART.value, ReportType.DATAFRAME.value])

    if reporting == ReportType.CHART.value:
        template = None
        choose_template = st.checkbox("Choose template?")
        if choose_template:
            template = st.selectbox(label="Template", options=templates)

if reporting == ReportType.CHART.value:
    draw_correlation(data=clean.select(metric_cols), template=template)
else:
    st.write(data.head())
