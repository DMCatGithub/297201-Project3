import pandas as pd
import streamlit as st
import calendar
import datetime
import time
from math import radians, sin, cos, sqrt, atan2


# Example code from meteostat site - NOT USED - 
# import streamlit as st
# import meteostat as ms
# # from ms import Point, Daily

# import pandas as pd
# from datetime import datetime

# st.title("Historical Weather Dashboard")

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



# Meteo Stat code
# import streamlit as st
# from datetime import date
# import meteostat as ms

# Test code for meteostat values

# POINT = ms.Point(50.1155, 8.6842, 113)
# START = date(2018, 1, 1)
# END = date(2018, 1, 15)

# stations = ms.stations.nearby(POINT, limit=4)
# ts = ms.daily(stations, START, END)
# df = ms.interpolate(ts, POINT).fetch()

# Output the values instead of plotting
# st.subheader("Daily Weather Values")
# st.dataframe(df)

# UV test code
# import streamlit as st
# import requests
# import pandas as pd

# # st.title("UV API Test - CurrentUVIndex.com")

# def get_uv(lat, lon):
#     url = f"https://currentuvindex.com/api/v1/uvi?latitude={lat}&longitude={lon}"

#     try:
#         r = requests.get(url, timeout=10)
#         data = r.json()

#         st.write("### Raw API Response")
#         st.json(data)

#         # 1. Try forecast for 1 PM
#         forecast = data.get("forecast", [])
#         df_f = pd.DataFrame(forecast)

#         if not df_f.empty:
#             df_f["time"] = pd.to_datetime(df_f["time"])
#             uv_1pm = df_f[df_f["time"].dt.hour == 13]
#             if not uv_1pm.empty:
#                 return float(uv_1pm["uvi"].iloc[0])

#         # 2. Try history for 1 PM
#         history = data.get("history", [])
#         df_h = pd.DataFrame(history)

#         if not df_h.empty:
#             df_h["time"] = pd.to_datetime(df_h["time"])
#             uv_1pm = df_h[df_h["time"].dt.hour == 13]
#             if not uv_1pm.empty:
#                 return float(uv_1pm["uvi"].iloc[0])

#         # 3. Fallback: current UV
#         if "now" in data and "uvi" in data["now"]:
#             return float(data["now"]["uvi"])

#         return float("nan")

#     except Exception as e:
#         # st.error(f"Error: {e}")
#         return float("nan")


# -------------------------
# Streamlit UI
# -------------------------

# city = st.selectbox(
#     "Choose a test location",
#     ["Auckland", "New York", "London", "Mumbai"]
# )

# coords = {
#     "Auckland": (-36.8485, 174.7633),
#     "New York": (40.7128, -74.0060),
#     "London": (51.5074, -0.1278),
#     "Mumbai": (19.0760, 72.8777),
# }

# lat, lon = coords[city]

# if st.button("Test UV API"):
#     st.write(f"### Testing UV for {city}")
#     uv = get_uv(lat, lon)
#     st.metric("UV Index at 1 PM (or fallback)", uv)

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
import streamlit as st
from datetime import date
import meteostat as ms

st.title("Comfort Compass")
def weather_block(title, input_widget, priority_key):
    st.subheader(title)

    # Priority selector (horizontal segmented control)
    priority = st.segmented_control(
        f"{title} Priority",
        options=["Disabled", "Low Priority", "Medium Priority", "High Priority"],
        default="Medium Priority",
        key=priority_key
    )

    # If disabled → hide the slider and return None
    if priority == "Disabled":
        return None, priority, True

    # Otherwise show the input widget
    value = input_widget()

    return value, priority, False


def compute_overall_range(selected_tuple, range_map):
    if selected_tuple is None:
        return None, None

    low_cat, high_cat = selected_tuple

    low_min, _ = range_map[low_cat]
    _, high_max = range_map[high_cat]

    return low_min, high_max

uv_value, uv_priority, uv_disabled = weather_block(
    "UV Index",
    input_widget=lambda: st.slider(
        "Select preferred maximum UV index (see UV index guide below):",
        min_value=1,
        max_value=11,
        value=3,
        key="uv_slider"
    ),
    priority_key="uv_priority"
)

with st.expander("Show UV Index Guide"):

    uv_levels = [
        ("Low (1-2)", "Burn ~60 min — Minimal protection", "#3CB371", "black"),
        ("Moderate (3-5)", "Burn ~40 min — Protection recommended", "#FFD700", "black"),
        ("High (6-7)", "Burn ~30 min — Protection essential", "#FF8C00", "black"),
        ("Very High (8-10)", "Burn ~20 min — Extra protection needed", "#FF4500", "black"),
        ("Extreme (11+)", "Burn <15 min — Avoid sun exposure", "#9400D3", "black"),
    ]

    for title, desc, color, text_color in uv_levels:
        st.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:8px 12px;
                border-radius:6px;
                margin-bottom:6px;
                color:{text_color};
                font-weight:600;
                font-size:14px;">
                {title} — {desc}
            </div>
            """,
            unsafe_allow_html=True
        )

temp_value, temp_priority, temp_disabled = weather_block(
    "Temperature",
    input_widget=lambda: st.slider(
        "Select preferred temperature range (°C):",
        min_value=-10,
        max_value=50,
        value=(20, 25),
        key="temp_slider"
    ),
    priority_key="temp_priority"
)



wind_value, wind_priority, wind_disabled = weather_block(
    "Wind",
    input_widget=lambda: st.select_slider(
        "Select preferred wind category range:",
        options=[
            "Calm", "Light Air", "Light Breeze", "Gentle Breeze",
            "Moderate Breeze", "Fresh Breeze", "Strong Breeze"
        ],
        value=("Calm", "Light Breeze"),
        key="wind_slider"
    ),
    priority_key="wind_priority"
)

wind_ranges = {
    "Calm": (0, 2),
    "Light Air": (2, 5),
    "Light Breeze": (6, 11),
    "Gentle Breeze": (12, 19),
    "Moderate Breeze": (20, 28),
    "Fresh Breeze": (29, 38),
    "Strong Breeze": (39, 50)
}

wind_overall_min, wind_overall_max = compute_overall_range(
    wind_value,
    wind_ranges
)



rain_value, rain_priority, rain_disabled = weather_block(
    "Rain",
    input_widget=lambda: st.select_slider(
        "Select preferred rain level:",
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

rain_ranges = {
    "No Rain": (0, 0.2),
    "Light Rain": (0.2, 2.5),
    "Moderate Rain": (2.5, 7.6),
    "Heavy Rain": (7.6, 50)
}

rain_overall_min, rain_overall_max = compute_overall_range(
    rain_value,
    rain_ranges
)




humidity_value, humidity_priority, humidity_disabled = weather_block(
    "Humidity",
    input_widget=lambda: st.select_slider(
        "Select preferred humidity range:",
        options=[
            "Very Dry",
            "Dry",
            "Comfortable",
            "Humid",
            "Very Humid",
            "Extremely Humid"
        ],
        value=("Comfortable", "Humid"),
        key="humidity_slider"
    ),
    priority_key="humidity_priority"
)

humidity_ranges = {
    "Very Dry": (0, 30),
    "Dry": (30, 40),
    "Comfortable": (40, 60),
    "Humid": (60, 75),
    "Very Humid": (75, 90),
    "Extremely Humid": (90, 100)
}

humidity_overall_min, humidity_overall_max = compute_overall_range(
    humidity_value,
    humidity_ranges
)



cloud_value, cloud_priority, cloud_disabled = weather_block(
    "Cloud Cover",
    input_widget=lambda: st.select_slider(
        "Select preferred cloud cover:",
        options=[
            "Clear Sky",
            "Few Clouds",
            "Scattered Clouds",
            "Broken Clouds",
            "Overcast"
        ],
        value=("Clear Sky", "Few Clouds"),
        key="cloud_slider"
    ),
    priority_key="cloud_priority"
)

cloud_ranges = {
    "Clear Sky": (0, 1),
    "Few Clouds": (1, 3),
    "Scattered Clouds": (3, 5),
    "Broken Clouds": (5, 8),
    "Overcast": (8, 9)
}

cloud_overall_min, cloud_overall_max = compute_overall_range(
    cloud_value,
    cloud_ranges
)

# from meteostat import Point, Daily
# from datetime import datetime



# def get_weather(lat, lon, start, end):
#     location = Point(lat, lon)

#     data = Daily(location, start, end)
#     df = data.fetch()

#     if df.empty:
#         return None

#     return {
#         "Rain": df["prcp"].mean(),       # precipitation (mm)
#         "Wind": df["wspd"].mean(),    # wind speed (km/h)
#         "Humidity": df["rhum"].mean(),      # relative humidity (%)
#         "Cloud Cover": df["coco"].mean()    # cloud cover code (0–9)
#     }

# API  dropping values / not using
# weather_results = []

# # Loop through dataset_with_score_df (NOT df)
# for idx, row in dataset_with_score_df.iterrows():
#     lat = row["Latitude"]
#     lon = row["Longitude"]

#     weather = get_weather(lat, lon, start, end)

#     if weather is None:
#         weather_results.append({
#             "Rain": None,
#             "Wind": None,
#             "Humidity": None,
#             "Cloud Cover": None
#         })
#     else:
#         weather_results.append(weather)

# # Convert results to DataFrame
# weather_df = pd.DataFrame(weather_results)

# # Merge back into dataset_with_score_df
# dataset_with_score_df = pd.concat([dataset_with_score_df, weather_df], axis=1)

# dataset_with_score_df

# 3. Select travel mode
travel_mode = st.radio("How will you travel?",["Car", "Plane"])

travel_time = st.number_input(
    "Maximum travel time (hours)",
    min_value=1,
    max_value=12,
    value=5,
    step=1
)

# 4. Select travel month
# Set travel related variables
months = list(calendar.month_name)[1:]
selected_month = st.selectbox("What month do you plan to travel?", months)
current_year = datetime.datetime.now().year

travel_month = months.index(selected_month) + 1

AVG_CAR_SPEED = 80  # km/h
AVG_PLANE_SPEED = 800  # km/h

if travel_mode == "Car":
    travel_distance = travel_time * AVG_CAR_SPEED
else:
    travel_distance = travel_time * AVG_PLANE_SPEED

# 5. Select your country
# Make a sorted list of all unique countries
unique_countries = sorted(airports_unique_cities_df["Country"].dropna().unique())
Departure_Country = st.selectbox("Select your country",options=unique_countries, index=None, placeholder="Type to search...")

if not Departure_Country:
    st.stop()

# 6. Select from avaialble town/city in your country.
# Make sorted list of all towns in all countries
towns_in_selected_country = sorted(airports_unique_cities_df.loc[airports_unique_cities_df["Country"] == Departure_Country, "City"].dropna().unique())
Departure_City = st.selectbox("Select nearest town or city",options=towns_in_selected_country, index=None, placeholder="Type to search...")

if not Departure_City:
    st.stop()


# 7. Select preferred airport
# Only relevant if (1) Plane mode and (2) Multiple airports available in town selected
# Hide menu if car mode selected and automatically 


if travel_mode == "Car":
    # For car travel, automatically pick the first airport in the city
    airports_in_town = airports_df[
        (airports_df["Country"] == Departure_Country) &
        (airports_df["City"] == Departure_City) &
        (airports_df["IATA"].notna())
    ]

    if airports_in_town.empty:
        st.error("No airports found for this city.")
        st.stop()

    selected_airport_row = airports_in_town.iloc[0]
    # st.info(f"Car travel selected — automatically using nearest airport: {selected_airport_row['Airport']} ({selected_airport_row['IATA']})")

else:
    # PLANE MODE — show dropdown if multiple airports exist
    airports_in_town = airports_df[
        (airports_df["Country"] == Departure_Country) &
        (airports_df["City"] == Departure_City) &
        (airports_df["IATA"].notna())
    ]

    if len(airports_in_town) == 1:
        selected_airport_row = airports_in_town.iloc[0]
        # st.info(f"Only one airport available: {selected_airport_row['Airport']} ({selected_airport_row['IATA']})")
    else:
        airport_options = airports_in_town.apply(
            lambda row: f"{row['Airport']} ({row['IATA']})",
            axis=1
        )
        selected_option = st.selectbox("Select your preferred airport", options=airport_options)
        selected_airport_row = airports_in_town.iloc[airport_options.tolist().index(selected_option)]

Departure_Airport = selected_airport_row["IATA"]


# --- STOP HERE UNTIL USER CLICKS BUTTON ---
ready = st.button("Find destinations")

if not ready:
    st.stop()

  


# Function for working out distance to each location
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radius in km
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

#

def plane_destinations ():
# Make dataframe of all routes_from_df[Departure_Airport]
    routes_from_df = routes_df[routes_df["Departure_Airport"] == Departure_Airport][["Departure_Airport","Arrival_Airport"]].copy()

    for idx, row in routes_from_df.iterrows():

        Arrival_Airport = row["Arrival_Airport"]

        lat1 = airports_df.loc[airports_df["IATA"] == Departure_Airport, "Latitude"].iloc[0]
        lon1 = airports_df.loc[airports_df["IATA"] == Departure_Airport, "Longitude"].iloc[0]

        lat2 = airports_df.loc[airports_df["IATA"] == Arrival_Airport, "Latitude"].iloc[0]
        lon2 = airports_df.loc[airports_df["IATA"] == Arrival_Airport, "Longitude"].iloc[0]
        
        city = airports_df.loc[airports_df["IATA"] == Arrival_Airport, "City"].iloc[0]
        country = airports_df.loc[airports_df["IATA"] == Arrival_Airport, "Country"].iloc[0]
            
        distance = haversine(lat1, lon1, lat2, lon2)

        # Add new columns 
        routes_from_df.at[idx,"Latitude"] = lat2
        routes_from_df.at[idx,"Longitude"] = lon2
        routes_from_df.at[idx,"Distance"] = distance

        routes_from_df.at[idx,"City"] = city
        routes_from_df.at[idx,"Country"] = country

        routes_from_df.at[idx,"Travel_Month"] = travel_month
        routes_from_df.at[idx,"Current_year"] = current_year

        routes_from_df.at[idx,"Temp_hi"] = Temp_hi
        routes_from_df.at[idx,"Temp_lo"] = Temp_lo

        routes_from_df.at[idx,"UV_hi"] = UV_hi
        routes_from_df.at[idx,"UV_lo"] = UV_lo

    # routes_from_df

    # # Only routes within user target
    routes_for_user_df = routes_from_df.drop_duplicates(subset=["Arrival_Airport"])
    routes_for_user_df = routes_for_user_df[routes_from_df["Distance"] < travel_distance].sort_values("Distance").reset_index(drop=True)
  

    # # Sample 10 destinations from the list
    # sampled_routes_df = routes_for_user_df.sample(n=10, random_state=42)

    if len(routes_for_user_df) <= 10:
        sampled_routes_df = routes_for_user_df
    else:   
        sampled_routes_df = routes_for_user_df.sample(n=10)

    return sampled_routes_df


# Run function plane_destinations
sampled_routes_df = plane_destinations();

sampled_routes_df["Distance"] = sampled_routes_df["Distance"].round(0).astype(int).astype(str) + " km"

sampled_routes_df["Temp_hi"] = Temp_hi
sampled_routes_df["Temp_lo"] = Temp_lo

sampled_routes_df["UV_hi"] = UV_hi
sampled_routes_df["UV_lo"] = UV_lo

sampled_routes_df["Travel Month"] = travel_month
sampled_routes_df["Current year"] = current_year