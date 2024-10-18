from enum import Enum

import altair
import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

from common import MAXIMUMS, MEDIANS, MINIMUMS, options  # noqa: E402


@st.cache_resource
def load_time_data(boroughs: list[str], option: str) -> pl.DataFrame:
    data = pl.read_parquet(f"data/borough__{option}.parquet")

    return data.filter(pl.col("borough").is_in(boroughs))


with st.sidebar:
    option = st.selectbox(label="Filter by", options=options)


minimum = MINIMUMS[option]
maximum = MAXIMUMS[option]
value = (minimum, MEDIANS[option])

with st.sidebar:
    start_time, end_time = st.slider(f"Choose {option} range", minimum, maximum, value)  # type: ignore [call-overload]

boroughs = ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"]


selected_boroughs = st.multiselect("Boroughs you want to check", boroughs, boroughs)

COLUMNS = {
    "Number of Crashes": "count",
    "Number of persons killed": "number_of_persons_killed",
    "Number of persons injured": "number_of_persons_injured",
}

column = st.selectbox(label="Generate data for", options=COLUMNS.keys())

data = load_time_data(boroughs=selected_boroughs, option=option)
data = data.filter(pl.col(option).is_between(lower_bound=start_time, upper_bound=end_time))


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


""

with st.sidebar:
    reporting = st.selectbox(
        label="Output type",
        options=[ReportType.CHART.value, ReportType.DATAFRAME.value, ReportType.FILE_DOWNLOAD.value],
    )

if reporting == ReportType.CHART.value:
    with st.sidebar:
        visualization = st.selectbox(
            label="Visualize data as",
            options=[
                VisualizationType.LINE.value,
                VisualizationType.POINT.value,
                VisualizationType.BAR.value,
                VisualizationType.CIRCLE.value,
                VisualizationType.AREA.value,
            ],
        )
    if visualization == VisualizationType.LINE.value:
        st.line_chart(data=data, x=option, y=COLUMNS[column], color="borough")
    elif visualization == VisualizationType.AREA.value:
        st.area_chart(data=data, x=option, y=COLUMNS[column], color="borough")
    elif visualization == VisualizationType.BAR.value:
        st.bar_chart(data=data, x=option, y=COLUMNS[column], color="borough")
    elif visualization == VisualizationType.CIRCLE.value:
        st.scatter_chart(data=data, x=option, y=COLUMNS[column], color="borough", size=COLUMNS[column])
    else:
        chart = (
            altair.Chart(data=data)
            .mark_point()
            .encode(x=option, y=COLUMNS[column], color="borough", size=COLUMNS[column])
        ).interactive()
        st.altair_chart(chart, use_container_width=True)

elif reporting == ReportType.DATAFRAME.value:
    max_rows = 1000
    n_rows = st.number_input(label="Number of rows", min_value=1, max_value=max_rows, value=10)
    st.info(f"You can check at most {max_rows} rows here.", icon="ℹ️")
    st.dataframe(data=data.head(n=n_rows))
else:
    download_filename = f'{"_".join([borough.lower().replace(" ", "_") for borough in selected_boroughs])}_{column}_{start_time}_{end_time}.csv'
    st.download_button(label="Download", data=data.to_pandas().to_csv(), mime="text/csv", file_name=download_filename)
""
