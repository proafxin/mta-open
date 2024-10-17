import altair
import streamlit as st
from polars import read_parquet

st.set_page_config(page_title="12 Years of NY Motor Crash ", layout="wide")
st.title("New York Motor Vehicles Crash Data Insights")
""
""

data = read_parquet("data/processed.parquet")
url = "https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data"
st.link_button("Find details about the dataset here", url=url)
markdown = f"Data spans from {data['date'].min()} to {data['date'].max()}."  # type: ignore[str-bytes-safe]
st.markdown(markdown)

""
altair.themes.enable("dark")


#######################
# CSS styling
st.markdown(
    """
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    text-align: left;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""",
    unsafe_allow_html=True,
)


col = st.columns((2, 2), gap="small")


with col[0]:
    columns = data.columns
    st.subheader("Data Cleaning Policy")
    text = "There are many data points that are not properly labeled. Here are the policies used to clean this data."
    st.markdown(text)
    st.markdown(
        "* General principle: when considering a certain factor, all the points missing values for that factor are discarded."
    )
    st.markdown("* Example: if location is not present, the point is not considered for map plotting.")
    st.markdown(
        "* Locations are sometimes inaccurate. For example, there are coordinates with (0,0) values. These are considered **invalid**."
    )

    st.subheader("Navigation")
    with st.container():
        st.page_link(
            page="pages/Charts_and_Statistics.py", label="Visualize charts and get insights from statistics", icon="📊"
        )

    with st.container():
        st.page_link(page="pages/Data_Exploration.py", label="Explore data", icon="ℹ️")

    with st.container():
        st.page_link(page="pages/Maps.py", label="Generate heatmaps", icon="🌍")

    with st.container():
        st.page_link(page="pages/Timeseries_Charts.py", label="Get timeseries charts", icon="📈")


with col[1]:
    subcols = st.columns((0.5, 0.5), gap="small")
    with subcols[0]:
        st.header("Metadata")
        st.metric("Total number of crashes", data.shape[0])
        marked = data["borough"].drop_nulls().shape[0]
        st.metric("Location marked", marked)
        st.metric("Location unmarked", data.shape[0] - marked)
        invalid = read_parquet("data/invalid_coordinate.parquet")
        st.metric("Valid Locations", value=marked - invalid.shape[0])
        st.metric("Invalid locations", invalid.shape[0])

    with subcols[1]:
        st.header("Victims")
        st.metric("Total killed", data["number_of_persons_killed"].sum())
        st.metric("Total injured", data["number_of_persons_injured"].sum())
