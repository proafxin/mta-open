import altair
import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

data = pl.read_parquet("data/processed.parquet")
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


st.header("Safety Statistics")
safety_columns = ["year", "borough"]

status_readable_names = {"number_of_persons_killed": "death", "number_of_persons_injured": "injury"}

for safety_column in safety_columns:
    safety_statuses = ["number_of_persons_killed", "number_of_persons_injured"]
    safety_cols = st.columns((1,) * len(safety_statuses), gap="medium")

    for i, safety_status in enumerate(safety_statuses):
        with safety_cols[i]:
            st.subheader(f"By {safety_column} and {status_readable_names[safety_status]}")

            safety_data = (
                data.select([safety_column, safety_status])
                .drop_nulls()
                .group_by(safety_column)
                .agg(pl.col(safety_status).sum())
                .sort(by=safety_column)
            )
            st.dataframe(safety_data)
    ""


COLUMN_VALUES = {
    "year": range(2012, 2025),
    "borough": ["BRONX", "QUEENS", "BROOKLYN", "MANHATTAN", "STATEN ISLAND"],
    "month": range(1, 13),
    "hour": range(0, 23),
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


keys = list(inputs.keys())
if len(keys) > 0:
    subcols = st.columns((1, 1, 1), gap="small")
    filtered = data.filter(pl.col(keys[0]).eq(inputs[keys[0]]))

    for key in keys[1:]:
        filtered = filtered.filter(pl.col(key).eq(inputs[key]))

    with subcols[0]:
        st.metric(label="Crashes", value=filtered.shape[0])

    with subcols[1]:
        st.metric(label="Dead", value=filtered["number_of_persons_killed"].sum())

    with subcols[2]:
        st.metric(label="Injured", value=filtered["number_of_persons_injured"].sum())

st.header("Charts by a specific criteria")

count_columns = columns[:1] + columns[15:]

with st.expander("See charts"):
    column = st.selectbox("By criteria", count_columns)
    value_counts = data[column].drop_nulls().value_counts(sort=True)
    with st.container():
        chart = altair.Chart(value_counts).mark_circle().encode(x=column, y="count", size="count", color=column)
        st.altair_chart(altair_chart=chart)
