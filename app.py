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



# PLOT
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
