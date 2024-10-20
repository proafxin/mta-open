import altair
import streamlit as st

st.set_page_config(page_title="NY Motor Vehicles Crash", layout="wide")
st.title("12 Years of New York Motor Vehicles Crash: Statistics and Interactive Visualizations")

""


url = "https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data"


altair.themes.enable("dark")


tabs = st.tabs(["Learn More About Dataset", "Data Cleaning policy", "Risk Factor Calculation"])
with tabs[0]:
    st.link_button(label="New York Motor Vehicles Collisions and Crashes, Public Safety by NYPD", url=url)
    st.link_button(
        label="New York City Borough Boundaries",
        url="https://data.cityofnewyork.us/City-Government/Borough-Boundaries/tqmj-j8zm",
    )
    st.link_button(
        label="New York City Population By Borough",
        url="https://data.cityofnewyork.us/City-Government/New-York-City-Population-by-Borough-1950-2040/xywu-7bv9/data",
    )
    st.link_button(
        label="State zip codes of USA states boundaries", url="https://github.com/OpenDataDE/State-zip-code-GeoJSON"
    )
with tabs[1]:
    text = "There are many data points that are not properly labeled. Here are the policies used to clean this data."
    st.markdown(text)
    st.markdown(
        "* Null values are not considered e.g. if location is not present, the row is not considered for map plotting."
    )
    st.markdown(
        "* Obviously, context matters. Not all columns are considered for null filtering. Street names and contributing factors can often be left empty."
    )
    st.markdown(
        "* Locations are sometimes inaccurate. For example, there are coordinates with (0,0) values. These are considered **invalid**."
    )
    st.markdown(
        "* <10 locations had distances more than 3-5 times the average and showed up outside the map of New York. They were also considered invalid."
    )
    st.markdown("* Incorrectly labeled locations e.g. a crash occuring in Queens labeled as Bronx weren't discarded.")
with tabs[2]:
    st.markdown("* Number of casualty = Number of persons killed + Number of persons injured.")
    st.markdown("* For per unit metric calculation, all factors are considered per 10000 square area units.")
    st.markdown(
        "* Example for number of persons killed. First, number of persons killed in a borough is divided by it's area then multiplied by 10000."
    )
    st.markdown("* Risk factor = number of crash per 10000 square units + number of casualty per 10000 square units.")
