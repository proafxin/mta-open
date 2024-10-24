from enum import Enum

import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import streamlit as st
from plotly.io import templates
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")


class ReportType(str, Enum):
    CHART = "Chart"
    DATAFRAME = "Display data"
    FILE_DOWNLOAD = "Download full data"


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
    return pl.read_parquet("data/clean_map.parquet")


@st.cache_resource
def load_geo_data() -> gpd.GeoDataFrame:
    return gpd.read_parquet("data/nyc_projected.parquet")


@st.cache_resource
def load_borough_data() -> pl.DataFrame:
    data = pl.read_parquet("data/borough.parquet")
    data = data.with_columns((pl.col("number_of_casualty") / pl.col("number_of_crash")).alias("risk_factor"))

    return data


data = load_processed_data()
borough_data = load_borough_data()


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


with st.sidebar:
    reporting = st.selectbox(label="Output type", options=[ReportType.CHART.value, ReportType.DATAFRAME.value])

    if reporting == ReportType.CHART.value:
        template = None
        choose_template = st.checkbox("Choose template?")
        if choose_template:
            template = st.selectbox(label="Template", options=templates)

st.header("Raw Data")
st.markdown("This section displays the top 5 rows of the raw data after some processing.")
st.write(data.head())
st.write("Numer of entries in data:", data.shape[0], "Number of factors:", data.shape[1])
st.markdown("As you can see, there are some modifications in this data.")
st.markdown(
    "* `date` and `time` are the columns `crash_date` and `crash_time` with appropriate date and time types respectively."
)
st.markdown(
    "* `year`, `month`, `weekday` and `hour` columns are extracted from existing `date` and `time` columns. `weekday` starts at Monday (1) and ends in Sunday (7)."
)
st.markdown("* `number_of_casualty = number_of_persons_killed+number_of_persons_injured`")
st.markdown("* `code` is a unique mapping for boroughs.")
st.markdown(
    "* Columns involving vehicle factors such as `contributing_factor_vehicle_1` and `vehicle_type_code_1` are removed because they have too many missing values."
)
st.markdown("* `on_street_name`, `cross_street_name` and `off_street_name` are removed for the same reason.")

st.header("Number of Missing Values For Each Column")
null_count = data.null_count()
columns = null_count.columns

if reporting == ReportType.CHART.value:
    chart = px.bar(
        data_frame=pl.DataFrame({"columns": columns, "null_count": null_count.transpose()}),
        x="columns",
        y="null_count",
        color="columns",
        template=template,
    )
    chart.update_layout(yaxis_title="Number of values missing")
    st.plotly_chart(chart)
else:
    st.write(null_count)
with st.sidebar:
    filename = "number_of_missing_values.csv"
    st.download_button(
        label="Download number of missing value information",
        data=null_count.to_pandas().to_csv(),
        file_name=filename,
        mime="text/csv",
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

metric_cols = ["number_of_persons_killed", "number_of_persons_injured", "number_of_casualty", "number_of_crash"]

hour_cols = st.columns((1,) * 2, gap="small")
with st.sidebar:
    st.download_button(
        label="Download hour count data",
        data=hour_counts.to_pandas().to_csv(),
        file_name="hourly.csv",
        mime="text/csv",
    )
if reporting == ReportType.DATAFRAME.value:
    st.write(hour_counts)
else:
    st.bar_chart(data=hour_counts, x="hour", y="count", height=400, color="hour", y_label="Crash count by hour")
st.write(
    "It is safe to say 1-6 AM e.g. night time are the safest to drive as these 6 hours have the lowest 6 counts of crashes. On the other hand, 4-5 PM are the riskiest with the highest counts."
)

st.header("What weekdays are the safest?")
weekday_cols = st.columns((1,) * 2, gap="small")
if reporting == ReportType.DATAFRAME.value:
    st.write(weekday_counts)
else:
    st.bar_chart(data=weekday_counts, x="weekday", y="count", color="weekday", y_label="Weekay counts")
st.write(
    "Weekends have the minimum number of crashes, specially Sunday. On the other hand, Friday sees the most number of crashes."
)
with st.sidebar:
    st.download_button(
        label="Download weekday data",
        data=weekday_counts.to_pandas().to_csv(),
        mime="text/csv",
        file_name="weekday.csv",
    )

st.header("Safest Year?")
year_counts = data["year"].drop_nulls().value_counts().sort(by=["count"])
year_cols = st.columns((1,) * 2, gap="small")
if reporting == ReportType.DATAFRAME.value:
    st.write(year_counts)
else:
    st.bar_chart(data=year_counts, x="year", y="count", color="year", y_label="Crash count by year")
st.write(
    "The most number of crashes were recorded in 2016-18. It seems the number is consistently low after 2020. As of 22 October 2024, 2024 hasn't ended yet so data is incomplete for 2024."
)
with st.sidebar:
    st.download_button(
        label="Download yearly data", data=year_counts.to_pandas().to_csv(), mime="text/csv", file_name="yearly.csv"
    )

st.header("Overall Borough Safety")
borough_counts = data["borough"].drop_nulls().value_counts().sort(by=["count"])
borough_cols = st.columns((1,) * 2, gap="small")
if reporting == ReportType.DATAFRAME.value:
    st.write(borough_counts)
else:
    chart = px.bar(data_frame=borough_counts, x="borough", y="count", color="borough", template=template)
    chart.update_layout(yaxis_title="Crash count by borough")
    st.plotly_chart(chart)
with st.sidebar:
    st.download_button(
        label="Download borough data",
        data=borough_counts.to_pandas().to_csv(),
        mime="text/csv",
        file_name="borough.csv",
    )
st.write(
    "Apparently, Staten Island is the safest. However, it is also the smallest and has the lowest population. This prompts us to take area and population into consideration. However, there is no standard method to use them to normalize for assessing risks. Therefore, the best indicator we have is the number of crashes for each borough. This is actually a very sensible number for understanding risks. Yes, higher population density should lead to more accidents but that alone is not the contributing factor. One can argue road and transportation laws or average people's habit on the road contribute more to these incidents. Thus no factor is really decisive and all important and the only invariant is the frequency of crashes that happen. This can be considered as a metric of the `civility` of the people living in a borough."
)
st.write(
    "Following the dichotomy (or dilemma whatever you want to call it), we define risk factor as the following: `risk_factor = (number of persons killed+number of persons injured)/(number of crashes)`"
)
st.write(
    "This way, we are trying to normalize the casualty number against the number of crashes. It is not unreasonable to expect that more civility, stricter laws and tendency to follow traffic rules lead to less dangerous accidents. Thus, even if there are more people or larger area to contribute to crashes, we are hoping that the number of crashes will reflect the result of these factors (these crashes are the consequences of the contributions from these factors in the first place so it doesn't make much sense to make the risk calculating model unnecessarily complex)."
)
geo_data = load_geo_data()


metric_cols = ["distance", "number_of_persons_killed", "number_of_persons_injured", "number_of_casualty"]

st.header("Risk Assessment")

if reporting == ReportType.DATAFRAME.value:
    st.write(borough_data)
else:
    chart = px.bar(data_frame=borough_data, x="borough", y="risk_factor", template=template, color="borough")
    chart.update_layout(yaxis_title="Risk factor")
    st.plotly_chart(chart)
with st.sidebar:
    st.download_button(
        label="Download borough risk factor data",
        data=borough_data.to_pandas().to_csv(),
        mime="text/csv",
        file_name="borough_risk_factor.csv",
    )
st.write("According to this, `Manhattan` is the safest and `Staten Island` is the second safest.")
