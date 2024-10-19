import plotly.express as px
import polars as pl
import streamlit as st

st.set_page_config(layout="wide")


st.title("Metrics and Statistical Correlation Between Incidents")


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


def draw_correlation(data: pl.DataFrame, template: str | None = None) -> None:
    st.subheader(f"Correlation between incidents by {column}")
    df_pandas = data.drop(column).to_pandas()
    df_pandas.columns = [col.split("_")[-1].capitalize() for col in df_pandas.columns]  # type: ignore
    corr = df_pandas.corr()  # type: ignore [assignment]
    fig = px.imshow(corr, text_auto=True, aspect="auto", template=template)
    st.plotly_chart(fig, theme="streamlit")


with st.sidebar:
    templates = ["plotly", "ggplot2", "seaborn", "simple_white", "none"]
    choose_template = st.checkbox("Choose template?")
    template = None
    if choose_template:
        template = st.selectbox(label="Template", options=templates)

by = ["borough", "year"]


COLUMN_VALUES = {
    "year": range(2012, 2025),
    "borough": ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"],
    "month": range(1, 13),
    "hour": range(0, 24),
}

st.header("Statistics by Multiple Criteria")


filtered = pl.DataFrame()

inputs = {}

selectable_columns = list(COLUMN_VALUES.keys())
cols = st.columns((1,) * len(selectable_columns))


for i, column in enumerate(selectable_columns):
    with cols[i]:
        select = st.checkbox(label=f"Choose {column}?", value=True)

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

    metric_cols = ["number_of_persons_killed", "number_of_persons_injured", "number_of_casualty", "count"]
    metric_cols = sorted(metric_cols)

    subcols = st.columns((1,) * len(metric_cols), gap="small")

    for i, col in enumerate(metric_cols):
        with subcols[i]:
            st.metric(" ".join(col.split("_")).capitalize(), filtered[col].sum())

st.header("Correlation")

column = st.selectbox(label="Select", options=by)

data = load_data(column=column)

draw_correlation(data=data, template=template)

with st.sidebar:
    st.download_button(
        label=f"Correlation data for {column}s",
        data=data.to_pandas().to_csv(),
        mime="text/csv",
        file_name=f"correlation_{column}.csv",
    )
