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

# ***************************************************
# SLiders and selectors
# priority_map = {
#     "Low Priority": 0.3,
#     "Medium Priority": 0.6,
#     "High Priority": 1.0
# }

# priority_choice = st.selectbox(
#     "Priority",
#     ["Low Priority", "Medium Priority", "High Priority"],
#     index=1
# )

# # priority_weight = priority_map[priority_choice]




# # temp
# st.subheader("Temperature")
# temp_value = st.slider("Preferred Temperature (°C)", min_value=-10, max_value=40, value=(21,25))
# temp_priority = st.selectbox("Temperature Priority", ["Low Priority", "Medium Priority", "High Priority"])
# temp_weight = priority_map[temp_priority]

# # Wind speed
# st.subheader("Wind Speed")
# wind_speed = st.slider("Preferred Wind Speed (km/h)", min_value=0, max_value=50, value=(0,10))
# wind_priority = st.selectbox("Wind Priority", ["Low Priority", "Medium Priority", "High Priority"])
# wind_weight = priority_map[wind_priority]



# # Rain
# st.subheader("Rain Preference")

# rain_choice = st.radio(
#     "Prefered maximum amount of rain:",
#     ["No Rain", "Light Rain", "Moderate Rain", "Heavy Rain"]
# )

# rain_priority = st.selectbox("Rain Priority", ["Low Priority", "Medium Priority", "High Priority"])
# rain_weight = priority_map[rain_priority]

# # rain_score_map = {
# #     "No Rain": 100,
# #     "Light Rain": 70,
# #     "Moderate Rain": 40,
# #     "Heavy Rain": 10
# # }

# rain = st.select_slider(
#     "Rain Level",
#     options=["No Rain", "Light Rain", "Moderate Rain", "Heavy Rain"]
# )

# rain_score = rain_score_map[rain_choice]

# # humid
# st.subheader("Humidity")
# humidity_value = st.slider("Preferred Humidity (%)", min_value=0, max_value=100, value=(40,60))
# humidity_priority = st.selectbox("Humidity Priority", ["Low Priority", "Medium Priority", "High Priority"])
# humidity_weight = priority_map[humidity_priority]

# # humid2
# humidity_choice = st.radio(
#     "Humidity Level",
#     ["Very Dry", "Dry", "Comfortable", "Humid", "Very Humid"]
# )

# humidity_priority = st.selectbox("Humidity Priority2", ["Low Priority", "Medium Priority", "High Priority"])
# humidity_weight = priority_map[humidity_priority]


# # cloud
# st.subheader("Cloud Cover")
# cloud_value = st.radio(
#     "Select prefered cloud cover:",
#     ["Clear Sky", "Few Clouds", "Scattered Clouds", "Broken Clouds", "Overcast"]
# )

# cloud_priority = st.selectbox("Cloud Cover Priority", ["Low Priority", "Medium Priority", "High Priority"])
# cloud_weight = priority_map[cloud_priority]

# rain_score_map = {
#     "  0% Clear Sky": 100,
#     " 25% Few Clouds": 70,
#     " 50% Scattered Clouds": 40,
#     " 75% Broken Clouds": 10
#     "100% Overcast": 10
# }

# NEW CODE

def weather_block(
    title,
    input_widget,
    priority_key
):
    st.subheader(title)

    # Priority selector (now includes Disabled)
    priority = st.selectbox(
        f"{title} Priority",
        ["Disabled", "Low Priority", "Medium Priority", "High Priority"],
        key=priority_key
    )

    # If disabled → hide the slider and return None
    if priority == "Disabled":
        return None, priority, True

    # Otherwise show the input widget
    value = input_widget()

    return value, priority, False


temp_value, temp_priority, temp_disabled = weather_block(
    "Temperature",
    input_widget=lambda: st.slider(
        "Preferred Temperature (°C)",
        min_value=-10,
        max_value=50,
        value=(21, 25),
        key="temp_slider"
    ),
    priority_key="temp_priority"
)



wind_value, wind_priority, wind_disabled = weather_block(
    "Wind",
    input_widget=lambda: st.select_slider(
        "Wind Category Range",
        options=[
            "Calm", "Light Air", "Light Breeze", "Gentle Breeze",
            "Moderate Breeze", "Fresh Breeze", "Strong Breeze"
        ],
        value=("Light Air", "Moderate Breeze"),
        key="wind_slider"
    ),
    priority_key="wind_priority"
)


rain_value, rain_priority, rain_disabled = weather_block(
    "Rain",
    input_widget=lambda: st.select_slider(
        "Rain Level",
        options=[
            "No Rain",
            "Light Rain",
            "Moderate Rain",
            "Heavy Rain"
        ],
        value=("No Rain", "Light Rain"),
        key="rain_slider"
    ),
    priority_key="rain_priority"
)




humidity_value, humidity_priority, humidity_disabled = weather_block(
    "Humidity",
    input_widget=lambda: st.select_slider(
        "Humidity Range",
        options=[
            "Very Dry",
            "Dry",
            "Comfortable",
            "Humid",
            "Very Humid",
            "Extremely Humid"
        ],
        value=("Dry", "Humid"),
        key="humidity_slider"
    ),
    priority_key="humidity_priority"
)



cloud_value, cloud_priority, cloud_disabled = weather_block(
    "Cloud Cover",
    input_widget=lambda: st.select_slider(
        "Cloud Cover Range",
        options=[
            "Clear Sky",
            "Few Clouds",
            "Scattered Clouds",
            "Broken Clouds",
            "Overcast"
        ],
        value=("Few Clouds", "Broken Clouds"),
        key="cloud_slider"
    ),
    priority_key="cloud_priority"
)


