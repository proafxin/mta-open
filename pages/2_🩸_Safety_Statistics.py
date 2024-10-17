import polars as pl
import streamlit as st

st.set_page_config(layout="wide")


data = pl.read_parquet("data/processed.parquet")


st.header("Safety Statistics")
safety_columns = ["year", "month", "hour", "borough"]
safety_statuses = ["number_of_persons_killed", "number_of_persons_injured"]

status_readable_names = {
    "number_of_persons_killed": "death",
    "number_of_persons_injured": "injury",
    "total_damaged": "total damage",
}

safety_data = data.select(safety_columns + safety_statuses).drop_nulls()
# data = data.cast({safety_status: pl.Int64 for safety_status in safety_statuses})

safety_data = safety_data.with_columns(pl.sum_horizontal(safety_statuses).alias("total_damaged"))
safety_statuses.append("total_damaged")

safety_cols = st.columns((1,) * len(safety_statuses), gap="small")

for i, safety_status in enumerate(safety_statuses):
    with safety_cols[i]:
        for column in safety_columns[:-1]:
            st.subheader(f"{status_readable_names[safety_status].capitalize()} by {column} and borough")
            with st.expander("Click to see stats"):
                columns = ["borough", column]
                pivot = safety_data.pivot(on=columns, index=columns, values=[safety_status], aggregate_function="sum")
                pivot = pivot.with_columns(pl.coalesce(pl.col(pivot.columns[2:]).alias(safety_status)))
                pivot = pivot.select(columns + [safety_status])
                st.dataframe(pivot)
