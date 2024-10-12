import streamlit as st

from visualization.components import vehicles_data

st.write(f"## Number of incidents: {vehicles_data.shape[0]}")


st.write("## Count by columns")
option = st.selectbox("#### Select a column", vehicles_data.columns)

if option:
    st.bar_chart(data=vehicles_data[option].value_counts(), x=option, y="count")
