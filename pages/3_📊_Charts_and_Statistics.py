import altair
import polars as pl
import streamlit as st

st.set_page_config(layout="wide")


@st.cache_resource
def load_data() -> pl.DataFrame:
    return pl.read_parquet("data/processed.parquet")


data = load_data()
columns = data.columns
st.title("Statistics and Charts")

# st.header("Statistics by Year and Borough")
# cols = st.columns((1, 1), gap="small")


# with cols[0]:
#     with st.expander("Yearly Statistics"):
#         year = st.selectbox("Choose year", data["year"].unique())  # type: ignore [var-annotated]

#         filtered = data.filter(pl.col("year").eq(year))
#         subcols = st.columns((1, 1, 1), gap="small")
#         with subcols[0]:
#             st.metric(label="Crashes", value=filtered.shape[0])

#         with subcols[1]:
#             st.metric(label="Dead", value=filtered["number_of_persons_killed"].sum())

#         with subcols[2]:
#             st.metric(label="Injured", value=filtered["number_of_persons_injured"].sum())

# with cols[1]:
#     with st.expander("Borough Statistics"):
#         borough = st.selectbox("Choose Borough", data["borough"].drop_nulls().unique())  # type: ignore [var-annotated]

#         filtered = data.filter(pl.col("borough").eq(borough))
#         subcols = st.columns((1, 1, 1), gap="small")
#         with subcols[0]:
#             st.metric(label="Crashes", value=filtered.shape[0])

#         with subcols[1]:
#             st.metric(label="Dead", value=filtered["number_of_persons_killed"].sum())

#         with subcols[2]:
#             st.metric(label="Injured", value=filtered["number_of_persons_injured"].sum())


""


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
        select = st.checkbox(label=f"Choose {column}?")

        if select:
            criteria = st.selectbox(label=f"Select {column}", options=COLUMN_VALUES[column])  # type: ignore [var-annotated]
            inputs[column] = criteria

        elif column in inputs:
            inputs.pop(column)


def form_filename(keys: list[str], on: list[str]) -> str:
    filename = "__".join(sorted(keys))
    filename = f"data/{filename}.parquet"

    return filename


@st.cache_resource
def load_stats(keys: list[str]) -> pl.DataFrame:
    filename = form_filename(keys=keys, on=["number_of_persons_killed", "number_of_persons_injured", "total_damage"])

    return pl.read_parquet(filename)


keys = list(inputs.keys())
if len(keys) > 0:
    stats = load_stats(keys=keys)

    filtered = stats.filter(pl.col(keys[0]).eq(inputs[keys[0]]))

    for key in keys[1:]:
        filtered = filtered.filter(pl.col(key).eq(inputs[key]))

    metric_cols = ["number_of_persons_killed", "number_of_persons_injured", "total_damage", "count"]
    metric_cols = sorted(metric_cols)
    for row in filtered.to_dicts():
        subcols = st.columns((1,) * len(metric_cols), gap="small")

        for i, col in enumerate(metric_cols):
            with subcols[i]:
                st.metric(" ".join(col.split("_")).capitalize(), row[col])


st.header("Charts by a specific criteria")

count_columns = columns[:1] + columns[15:]

with st.expander("See charts"):
    column = st.selectbox("By criteria", count_columns)
    value_counts = data[column].drop_nulls().value_counts(sort=True)
    with st.container():
        chart = altair.Chart(value_counts).mark_circle().encode(x=column, y="count", size="count", color=column)
        st.altair_chart(altair_chart=chart)
