import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

from visualization.components import vehicles_data  # noqa: E402

event_type = "Event_Type"

st.write("# Interactive Visualization of Vehicle Crash Data")

st.write("## Sample Data")
st.dataframe(vehicles_data.head())

st.write(f"### Total data points: {vehicles_data.shape[0]}")

drop_columns = [
    "Contributing_Factor_2_Description",
    "Contributing_Factor_1_Description",
    "Partial_VIN",
    "Case_Vehicle_ID",
]
vehicles_data = vehicles_data.drop(drop_columns)

vehicles_data = vehicles_data.filter(pl.col(event_type).is_not_null())
collision = vehicles_data.filter(pl.col(event_type).str.contains("Collision"))

st.write("## Count by columns")
column = st.selectbox("Select a column", vehicles_data.columns)
st.bar_chart(data=vehicles_data[column].value_counts(), x=column, y="count", color=column)

st.write("### Event counts")
st.dataframe(vehicles_data[event_type].value_counts())

crashes = vehicles_data.filter(~(pl.col(event_type).str.contains("Not")))
crashes = crashes.filter(~(pl.col(event_type).str.contains("Non")))
crashes = crashes.filter(~(pl.col(event_type).str.contains("Unknown")))
st.write(f"## Total crash incidents: {crashes.shape[0]}")
st.write("## Sample crash events.")
st.dataframe(crashes.head())

st.write("## Crashes by event type")
event_selection = st.selectbox(label="Select an event type", options=crashes[event_type].unique().to_list())

if event_selection:
    st.bar_chart(data=crashes[event_type].value_counts(), x=event_type, y="count", color=event_type)
