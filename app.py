# import streamlit as st
# import meteostat as ms
# from ms import Point, Daily

# import pandas as pd
# from datetime import datetime

# st.title("🌦️ Historical Weather Dashboard")

# # 1. User inputs for location and date range
# st.sidebar.header("Location & Date Settings")
# lat = st.sidebar.number_input("Latitude", value=-36.8485, format="%.4f") # Default: Auckland
# lon = st.sidebar.number_input("Longitude", value=174.7633, format="%.4f") # Default: Auckland

# start_date = st.sidebar.date_input("Start Date", datetime(2025, 1, 1))
# end_date = st.sidebar.date_input("End Date", datetime(2025, 12, 31))

# # 2. Fetch and cache weather data
# @st.cache_data
# def load_weather_data(latitude, longitude, start, end):
#     # Create Meteostat Point object (lat, lon, elevation)
#     location = ms.Point(latitude, longitude)
#     # location = meteostat.Point(latitude, longitude)

    
#     # Fetch data
#     data = ms.Daily(location, start, end)
#     # data = meteostat.Daily(location, start, end).fetch()
#     df = data.fetch()
#     return df

# if st.sidebar.button("Fetch Data"):
#     with st.spinner("Downloading climate data..."):
#         df = load_weather_data(lat, lon, start_date, end_date)
        
#         if df.empty:
#             st.warning("No data found for this location and date range. Try a different location or date.")
#         else:
#             st.success("Data loaded successfully!")
            
#             # Display raw data in an expander
#             with st.expander("View Raw Data"):
#                 st.dataframe(df)
                
#             # 3. Streamlit Metrics
#             st.subheader(f"Weather Summary")
#             col1, col2, col3 = st.columns(3)
#             col1.metric("Avg Temperature", f"{df['tavg'].mean():.1f}°C")
#             col2.metric("Max Temperature", f"{df['tmax'].max():.1f}°C")
#             col3.metric("Min Temperature", f"{df['tmin'].min():.1f}°C")
            
#             # 4. Interactive Charts
#             st.subheader("Temperature Trends")
#             st.line_chart(df[['tavg', 'tmin', 'tmax']])



# Meteo Stat test code
import streamlit as st
from datetime import date
import meteostat as ms

st.title("Old Meteostat API – Values Only")

# Your original code — unchanged
POINT = ms.Point(50.1155, 8.6842, 113)
START = date(2018, 1, 1)
END = date(2018, 1, 15)

stations = ms.stations.nearby(POINT, limit=4)
ts = ms.daily(stations, START, END)
df = ms.interpolate(ts, POINT).fetch()

# Output the values instead of plotting
st.subheader("Daily Weather Values")
st.dataframe(df)

# Optional: show summary stats
st.subheader("Summary Statistics")
st.write(df.describe())

# UV test code
import streamlit as st
import requests
import pandas as pd

st.title("UV API Test – CurrentUVIndex.com")

def get_uv(lat, lon):
    url = f"https://currentuvindex.com/api/v1/uvi?latitude={lat}&longitude={lon}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        st.write("### Raw API Response")
        st.json(data)

        # 1. Try forecast for 1 PM
        forecast = data.get("forecast", [])
        df_f = pd.DataFrame(forecast)

        if not df_f.empty:
            df_f["time"] = pd.to_datetime(df_f["time"])
            uv_1pm = df_f[df_f["time"].dt.hour == 13]
            if not uv_1pm.empty:
                return float(uv_1pm["uvi"].iloc[0])

        # 2. Try history for 1 PM
        history = data.get("history", [])
        df_h = pd.DataFrame(history)

        if not df_h.empty:
            df_h["time"] = pd.to_datetime(df_h["time"])
            uv_1pm = df_h[df_h["time"].dt.hour == 13]
            if not uv_1pm.empty:
                return float(uv_1pm["uvi"].iloc[0])

        # 3. Fallback: current UV
        if "now" in data and "uvi" in data["now"]:
            return float(data["now"]["uvi"])

        return float("nan")

    except Exception as e:
        st.error(f"Error: {e}")
        return float("nan")


# -------------------------
# Streamlit UI
# -------------------------

city = st.selectbox(
    "Choose a test location",
    ["Auckland", "New York", "London", "Mumbai"]
)

coords = {
    "Auckland": (-36.8485, 174.7633),
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Mumbai": (19.0760, 72.8777),
}

lat, lon = coords[city]

if st.button("Test UV API"):
    st.write(f"### Testing UV for {city}")
    uv = get_uv(lat, lon)
    st.metric("UV Index at 1 PM (or fallback)", uv)
