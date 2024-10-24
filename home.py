import altair
import streamlit as st

st.set_page_config(page_title="NY Motor Vehicles Crash", layout="wide")
st.title("12 Years of New York Motor Vehicles Crash: Statistics and Interactive Visualizations")

""


st.header("What This Application Is")
st.markdown(
    "For the area and population New York has, the number of crashes that occur is conspicuously flagrant. This application is a comprehensive collection of statistical dashboards, metrics and interactive visualizations on New York's last 12 years worth of motor vehicle crash data. The primary objective is to provide actionable intelligence to reduce the number of crashes and mitigate the impact as much as possible."
)
st.markdown("Some usecases of this application include but are not limited to")
st.markdown("* Providing subjectively unbiased insights into these crashes.")
st.markdown("* Determining safest and riskiest locations based on reasonable metrics dependent on geography.")
st.markdown(
    "* Features to checkout statistics and metrics juxtaposed with the user's custom parameters by the date, location and time of the user's choosing."
)
st.markdown("* Allowing the user to interact with the data and visualize them using charts and maps.")
st.markdown(
    "* Providing the user with the statistical data  directly in case they want to analyze it themselves and draw their own conclusions."
)


url = "https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data"


altair.themes.enable("dark")


tabs = st.tabs(["Learn More About Dataset", "Data Cleaning policy"])
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
