import streamlit as st

st.set_page_config(layout="wide")
st.title("Interactive Visualization of Vehicle Crash Data")

from visualization.components import vehicles_crash_data  # noqa: E402

st.write("# Data Cleaning and Initial Analysis")
data_load_state = st.text("Loading data...")
data = vehicles_crash_data()
data_load_state.text("Loading data...done!")

st.subheader("Sample data")
st.dataframe(data.head())

st.write(f"#### Total data points: {data.shape[0]}")
st.write(f"#### Number of variables: {data.shape[1]}")

st.subheader("Count by variables")
count_columns = data.columns[2:3] + data.columns[7:]
column = st.selectbox("Select a column", count_columns)
st.dataframe(data[column].value_counts())
