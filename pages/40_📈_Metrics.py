from enum import Enum

import altair
import plotly.express as px
import polars as pl
import streamlit as st
from plotly.io import templates

st.set_page_config(layout="wide")


st.title("Metrics and Statistical Correlation")


class ReportType(str, Enum):
    CHART = "Chart"
    DATAFRAME = "Display data"
    FILE_DOWNLOAD = "Download full data"


class VisualizationType(str, Enum):
    LINE = "Line"
    POINT = "Point"
    AREA = "Area"
    CIRCLE = "Circle"
    BAR = "Bar"


def form_filename(keys: list[str], on: list[str]) -> str:
    filename = "__".join(sorted(keys))
    filename = f"data/{filename}.parquet"

    return filename


@st.cache_resource
def load_stats(keys: list[str]) -> pl.DataFrame:
    filename = form_filename(
        keys=keys, on=["number_of_persons_killed", "number_of_persons_injured", "number_of_casualty"]
    )

    return pl.read_parquet(filename)


@st.cache_resource
def load_data(column: str) -> pl.DataFrame:
    return pl.read_parquet(f"data/{column}.parquet")


@st.cache_resource
def load_borough_metrics() -> pl.DataFrame:
    return pl.read_parquet("data/per_unit.parquet")


def draw_correlation(data: pl.DataFrame, template: str | None = None) -> None:
    st.subheader(f"Correlation between incidents by {column}")
    df_pandas = data.drop(column).to_pandas()
    df_pandas.columns = [col.split("_")[-1].capitalize() for col in df_pandas.columns]  # type: ignore
    corr = df_pandas.corr()  # type: ignore [assignment]
    fig = px.imshow(corr, text_auto=True, aspect="auto", template=template)
    st.plotly_chart(fig, theme="streamlit")


by = ["borough", "year"]


COLUMN_VALUES = {
    "year": range(2012, 2025),
    "borough": ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"],
    "month": range(1, 13),
    "hour": range(0, 24),
}

borough_metrics = load_borough_metrics()
metric_cols = ["number_of_persons_killed", "number_of_persons_injured", "number_of_casualty", "number_of_crash"]

with st.sidebar:
    reporting = st.selectbox(label="Output type", options=[ReportType.CHART.value, ReportType.DATAFRAME.value])

    if reporting == ReportType.CHART.value:
        template = None
        choose_template = st.checkbox("Choose template?")
        if choose_template:
            template = st.selectbox(label="Template", options=templates)


for column in metric_cols:
    borough_metrics = borough_metrics.with_columns(
        pl.col(column).cast(pl.Float64) * 10000 / pl.col("area").alias(column)
    )

borough_metrics = borough_metrics.sort(by=["number_of_casualty", "number_of_crash"])
borough_metrics = borough_metrics.with_columns(
    pl.sum_horizontal("number_of_casualty", "number_of_crash").alias("risk_factor")
)

columns = [
    "number_of_crash",
    "number_of_persons_killed",
    "number_of_persons_injured",
    "number_of_casualty",
    "risk_factor",
]
columns_readable = [col.capitalize().replace("_", " ") for col in columns]
COLUMN_MAP = {col1: col2 for col1, col2 in zip(columns_readable, columns)}

st_cols = st.columns((1.4, 1), gap="small")

with st_cols[0]:
    st.header("Risk per 10000 Square Area Unit")

    if reporting == ReportType.DATAFRAME.value:
        st.write(borough_metrics)
    else:
        x_col = "borough"
        with st.sidebar:
            visualization = st.selectbox(
                label="Visualize metrics as",
                options=[
                    VisualizationType.CIRCLE.value,
                    VisualizationType.BAR.value,
                    VisualizationType.POINT.value,
                    VisualizationType.AREA.value,
                ],
            )
        selected_column = st.selectbox(label="Select", options=COLUMN_MAP.keys())
        column = COLUMN_MAP[selected_column]

        if visualization == VisualizationType.AREA.value:
            px_chart = px.area(data_frame=borough_metrics, x=x_col, y=column, color="borough", template=template)
        elif visualization == VisualizationType.BAR.value:
            px_chart = px.bar(data_frame=borough_metrics, x=x_col, y=column, color="borough", template=template)
        elif visualization == VisualizationType.CIRCLE.value:
            px_chart = px.scatter(
                data_frame=borough_metrics, x=x_col, y=column, color="borough", template=template, size=column
            )
        else:
            alt_chart = (
                altair.Chart(data=borough_metrics).mark_point().encode(x=x_col, y=column, color="borough", size=column)
            ).interactive()
            st.altair_chart(alt_chart, use_container_width=True)
        if "px_chart" in locals():
            st.plotly_chart(px_chart)

with st_cols[1]:
    st.header("Correlation")

    column = st.selectbox(label="Select", options=by)

    data = load_data(column=column)

    if reporting == ReportType.CHART.value:
        draw_correlation(data=data, template=template)
    else:
        st.write(data)

st.header("Statistics by Multiple Criteria")


filtered = pl.DataFrame()

inputs = {}

selectable_columns = list(COLUMN_VALUES.keys())
cols = st.columns((1,) * len(selectable_columns))

choice = False

for i, column in enumerate(selectable_columns):
    with cols[i]:
        select = st.checkbox(label=f"Choose {column}?", value=choice)
        choice = not choice

        if select:
            criteria = st.selectbox(label=f"Select {column}", options=COLUMN_VALUES[column])  # type: ignore [var-annotated]
            inputs[column] = criteria

        elif column in inputs:
            inputs.pop(column)


keys = list(inputs.keys())

if len(keys) > 0:
    stats = load_stats(keys=keys)

    filtered = stats.filter(pl.col(keys[0]).eq(inputs[keys[0]]))

    for key in keys[1:]:
        filtered = filtered.filter(pl.col(key).eq(inputs[key]))

    metric_cols = sorted(metric_cols)

    subcols = st.columns((1,) * len(metric_cols), gap="small")

    for i, col in enumerate(metric_cols):
        with subcols[i]:
            st.metric(" ".join(col.split("_")).capitalize(), filtered[col].sum())


with st.sidebar:
    filename = "borough_metrics.csv"
    st.download_button(
        label="Download metrics for boroughs",
        data=borough_metrics.to_pandas().to_csv(),
        file_name=filename,
        mime="text/csv",
    )
    st.download_button(
        label=f"Download correlation data for {column}s",
        data=data.to_pandas().to_csv(),
        mime="text/csv",
        file_name=f"correlation_{column}.csv",
    )
