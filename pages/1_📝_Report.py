import polars as pl
import streamlit as st

st.set_page_config(layout="wide")

st.title("High Level Report")
st.markdown(
    "The report in this page provides a comprehensive overall review of the crash incidents. A new acquiantance of this data should start from this page."
)


@st.cache_resource
def load_processed_data() -> pl.DataFrame:
    return pl.read_parquet("data/processed.parquet")


@st.cache_resource
def load_clean_data() -> pl.DataFrame:
    return pl.read_parquet("data/clean_data.parquet")


st.header("Raw Data")
st.markdown(
    "This section displays the top 5 rows of the raw data after some processing. The date and time columns are properly adjusted according to their time."
)
data = load_processed_data()
st.write(data.head())
st.write("Data shape:", data.shape)
st.markdown("As you can see, there are some new columns in this data.")
st.markdown(
    "* `date` and `time` are the columns `crash_date` and `crash_time` with appropriate date and time types respectively."
)
st.markdown(
    "* `year`, `month`, `weekday` and `hour` columns are extracted from existing `date` and `time` columns. `weekday` starts at Monday (1) and ends in Sunday (7)."
)
st.markdown("*`number_of_casualty = number_of_persons_killed+number_of_persons_injured`")

st.header("Number of Null Values For Each Column")
null_count = data.null_count()
columns = null_count.columns
st.write(null_count)
st.bar_chart(
    data=pl.DataFrame({"columns": columns, "null_count": null_count.transpose()}),
    x="columns",
    y="null_count",
    color="columns",
    use_container_width=True,
    height=300,
    y_label="Null count",
)
st.header("What time of the day is the riskiest?")
hour_counts = data["hour"].value_counts().sort(by=["count"])
weekday_counts = data["weekday"].value_counts().sort(by=["count"])


hour_cols = st.columns((1,) * 2, gap="small")
with st.container():
    with hour_cols[0]:
        st.write(hour_counts)
    with hour_cols[1]:
        st.bar_chart(data=hour_counts, x="hour", y="count", height=400, color="hour", y_label="Crash count by hour")
st.write(
    "It is safe to say 1-6 AM e.g. night time are the safest to drive as these 6 hours have the lowest 6 counts of crashes. On the other hand, 4-5 PM are the riskiest with the highest counts."
)

st.header("What weekdays are the safest?")
weekday_cols = st.columns((1,) * 2, gap="small")
with weekday_cols[0]:
    st.write(weekday_counts)
with weekday_cols[1]:
    st.bar_chart(data=weekday_counts, x="weekday", y="count", color="weekday", y_label="Weekay counts")
st.write(
    "Weekends have the minimum number of crashes, specially Sunday. On the other hand, Friday sees the most number of crashes."
)

st.header("Safest Year?")
year_counts = data["year"].drop_nulls().value_counts().sort(by=["count"])
year_cols = st.columns((1,) * 2, gap="small")
with year_cols[0]:
    st.write(year_counts)
with year_cols[1]:
    st.bar_chart(data=year_counts, x="year", y="count", color="year", y_label="Crash count by year", height=400)
st.write(
    "The most number of crashes were recorded in 2016-18. It seems the number is consistently low after 2020. At this time, 2024 hasn't ended yet so data is incomplete for 2024."
)

st.header("Overall Borough Safety")
borough_counts = data["borough"].drop_nulls().value_counts().sort(by=["count"])
borough_cols = st.columns((1,) * 2, gap="small")
with borough_cols[0]:
    st.write(borough_counts)
with borough_cols[1]:
    st.bar_chart(data=borough_counts, x="borough", y="count", color="borough", y_label="Crash count by borough")
st.write(
    "Clearly Staten Island is the safest and Brooklyn is the riskiest, however, area may also have something to do with it. For this reason, we will take a deeper look at this below."
)

st.header("Cleaned Data")
clean = load_clean_data()
st.write(clean.head())
st.write("Clean data shape:", clean.shape)
