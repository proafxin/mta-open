import streamlit as st

st.set_page_config(layout="wide")
st.title("Interactive Visualization of Vehicle Crash Data")

from visualization.components import vehicles_crash_data  # noqa: E402

st.write("# Data Cleaning and Initial Analysis")
data = vehicles_crash_data()
st.write("## Sample Data")
st.dataframe(data.head())

st.write(f"#### Total data points: {data.shape[0]}")
st.write(f"#### Number of variables: {data.shape[1]}")

st.write("## Count by variables")
count_columns = data.columns[2:3] + data.columns[7:]
column = st.selectbox("Select a column", count_columns)
st.dataframe(data[column].value_counts())
