from enum import Enum

import altair
import plotly.express as px
import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

from common import MAXIMUMS, MEDIANS, MINIMUMS, options  # noqa: E402


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


@st.cache_resource
def load_time_data(boroughs: list[str], option: str) -> pl.DataFrame:
    data = pl.read_parquet(f"data/borough__{option}.parquet")

    return data.filter(pl.col("borough").is_in(boroughs))


columns = ["number_of_crash", "number_of_persons_killed", "number_of_persons_injured", "number_of_casualty"]


@st.cache_resource
def load_cumulative(column: str) -> pl.DataFrame:
    cumulative = pl.read_parquet(f"data/{column}.parquet")
    for column in columns:
        cumulative = cumulative.with_columns(pl.col(column).cum_sum().alias(column))

    return cumulative


boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]


columns_readable = [col.capitalize().replace("_", " ") for col in columns]
COLUMN_MAP = {col1: col2 for col1, col2 in zip(columns_readable, columns)}

with st.sidebar:
    is_cumulative = st.checkbox("Cumulative data?")


selected_column = st.selectbox(label="Select", options=COLUMN_MAP.keys())
column = COLUMN_MAP[selected_column]

with st.sidebar:
    reporting = st.selectbox(label="Output type", options=[ReportType.CHART.value, ReportType.DATAFRAME.value])

if is_cumulative:
    if reporting == ReportType.CHART.value:
        with st.sidebar:
            templates = ["plotly", "ggplot2", "seaborn", "simple_white", "none"]
            choose_template = st.checkbox("Choose template?")
            template = None
            if choose_template:
                template = st.selectbox(label="Template", options=templates)

    by = st.selectbox(label="Cumulative by", options=["borough", "year"])

    cumulative = load_cumulative(column=by)
    data = cumulative.select(by, column)

    if reporting == ReportType.CHART.value:
        chart = px.bar(
            data_frame=data,
            x=by,
            y=column,
            template=template,
            labels=[by, column.capitalize().replace("_", " ")],
            text_auto=True,
            color=by,
        )
        st.plotly_chart(chart)
    elif reporting == ReportType.DATAFRAME.value:
        st.write(data)
    with st.sidebar:
        filename = f"cumulative_{by}_{column}.csv"
        st.download_button(
            label=f"Download cumulative data of {by} by {column.replace("_", " ")}",
            data=data.to_pandas().to_csv(),
            mime="text/csv",
            file_name=filename,
        )
else:
    with st.sidebar:
        option = st.selectbox(label="Filter by", options=options)

    minimum = MINIMUMS[option]
    maximum = MAXIMUMS[option]
    value = (minimum, MEDIANS[option])

    with st.sidebar:
        start_time, end_time = st.slider(f"Choose {option} range", minimum, maximum, value)  # type: ignore [call-overload]

    selected_boroughs = st.multiselect("Boroughs you want to check", boroughs, boroughs)

    data = load_time_data(boroughs=selected_boroughs, option=option)
    data = data.filter(pl.col(option).is_between(lower_bound=start_time, upper_bound=end_time))

    if reporting == ReportType.CHART.value:
        with st.sidebar:
            visualization = st.selectbox(
                label="Visualize data as",
                options=[
                    VisualizationType.BAR.value,
                    VisualizationType.LINE.value,
                    VisualizationType.POINT.value,
                    VisualizationType.CIRCLE.value,
                    VisualizationType.AREA.value,
                ],
            )
        if visualization == VisualizationType.LINE.value:
            st.line_chart(data=data, x=option, y=COLUMN_MAP[selected_column], color="borough")
        elif visualization == VisualizationType.AREA.value:
            st.area_chart(data=data, x=option, y=COLUMN_MAP[selected_column], color="borough")
        elif visualization == VisualizationType.BAR.value:
            st.bar_chart(data=data, x=option, y=COLUMN_MAP[selected_column], color="borough")
        elif visualization == VisualizationType.CIRCLE.value:
            st.scatter_chart(
                data=data, x=option, y=COLUMN_MAP[selected_column], color="borough", size=COLUMN_MAP[selected_column]
            )
        else:
            chart = (
                altair.Chart(data=data)
                .mark_point()
                .encode(x=option, y=COLUMN_MAP[selected_column], color="borough", size=COLUMN_MAP[selected_column])
            ).interactive()
            st.altair_chart(chart, use_container_width=True)

    elif reporting == ReportType.DATAFRAME.value:
        max_rows = 1000
        n_rows = st.number_input(label="Number of rows", min_value=1, max_value=max_rows, value=10)
        st.info(f"You can check at most {max_rows} rows here.", icon="ℹ️")
        st.dataframe(data=data.head(n=n_rows))
    with st.sidebar:
        download_filename = f'{"_".join([borough.lower().replace(" ", "_") for borough in selected_boroughs])}_{selected_column}_{start_time}_{end_time}.csv'
        st.download_button(
            label="Download", data=data.to_pandas().to_csv(), mime="text/csv", file_name=download_filename
        )
    ""
