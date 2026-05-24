import pandas as pd
import streamlit as st
import calendar
import datetime
import time
from math import radians, sin, cos, sqrt, atan2


# LOAD AIRPORTS: Turn airports.dat in dataframe airports_df
airports_df = pd.read_csv("airports.dat", header=None)
airports_df.columns = ["AirportID", "Airport", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude", "Altitude", "Timezone", "DST", "TZ", "Type", "Source"]

# Removeing duplicate cities in same country (Only want city to show once in selection)
airports_unique_cities_df = airports_df.drop_duplicates(subset=["Country", "City"])

# LOAD ROUTES: Turn routes.dat into dataframe routes_df
routes_df = pd.read_csv("routes.dat", header=None)
routes_df.columns = ["Airline", "AirlineID", "Departure_Airport", "Departure_AirportID", "Arrival_Airport", "Arrival_AirportID", "Codeshare", "Stops", "Equipment"]





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






# NEW CODE
import streamlit as st
from datetime import date
import meteostat as ms

st.title("Comfort Compass")
def weather_block(title, input_widget, priority_key, default_priority = "Skip This"):
    st.subheader(title)

    # Priority selector (horizontal segmented control)
    # priority = st.segmented_control(
    priority = st.pills(
        f"{title} Priority",
        options=["Skip This", "Low Priority", "Medium Priority", "High Priority"],
        default=default_priority,
        key=priority_key
    )

    # If Skip This → hide the slider and return None
    if priority == "Skip This":
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




temp_value, temp_priority, temp_disabled = weather_block(
    "Temperature",
    input_widget=lambda: st.slider(
        "Select preferred temperature range (°C):",
        min_value=-20,
        max_value=50,
        value=(20, 25),
        key="temp_slider"
    ),
    priority_key="temp_priority",
    default_priority="Medium Priority"
)

if not temp_disabled:
    temp_overall_min = temp_value[0]
    temp_overall_max = temp_value[1]

uv_categories = [
    "Low (1-2)",
    "Moderate (3-5)",
    "High (6-7)",
    "Very High (8-10)",
    "Extreme (11+)"
]

uv_value, uv_priority, uv_disabled = weather_block(
    "UV Index",
    input_widget=lambda: st.select_slider(
        "Select maximum UV category:",
        options=uv_categories,
        value="Moderate (3-5)",
        key="uv_slider"
    ),
    priority_key="uv_priority"
)

if not uv_disabled:
    uv_overall_min = "Low (1-2)"   # fixed
    uv_overall_max = uv_value      # user-selected



with st.expander("Show UV Index Guide"):

    uv_levels = [
        ("Low (1–2)", "Burn ~60 min — Minimal protection", "#E8F5E9", "black"),
        ("Moderate (3–5)", "Burn ~40 min — Protection recommended", "#FFF9C4", "black"),
        ("High (6–7)", "Burn ~30 min — Protection essential", "#FFE0B2", "black"),
        ("Very High (8–10)", "Burn ~20 min — Extra protection needed", "#FFCCBC", "black"),
        ("Extreme (11+)", "Burn <15 min — Avoid sun exposure", "#F8BBD0", "black"),
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

with st.expander("Show Humidity Guide"):

    humidity_levels = [
        ("Very Dry (0–30%)", "Desert‑dry — uncomfortable", "#FFF9C4", "black"),
        ("Dry (30–40%)", "Crisp — slightly dry", "#FFE082", "black"),      
        ("Comfortable (40–60%)", "Ideal comfort zone", "#E8F5E9", "black"), 
        ("Humid (60–75%)", "Sticky — warm", "#BBDEFB", "black"),             
        ("Very Humid (75–90%)", "Heavy — tropical", "#90CAF9", "black"),       
        ("Extremely Humid (90–100%)", "Oppressive — rainforest‑like", "#64B5F6", "black"), 
    ]

    humidity_levels = [
        ("Very Dry (0–30%)", "Desert‑dry — uncomfortable", "#FFF9C4", "black"),   # pastel yellow
        ("Dry (30–40%)", "Crisp — slightly dry", "#FFE082", "black"),            # soft amber
        ("Comfortable (40–60%)", "Ideal comfort zone", "#E8F5E9", "black"),      # pastel mint green
        ("Humid (60–75%)", "Sticky — warm", "#BBDEFB", "black"),                 # light pastel blue
        ("Very Humid (75–90%)", "Heavy — tropical", "#90CAF9", "black"),         # medium pastel blue
        ("Extremely Humid (90–100%)", "Oppressive — rainforest‑like", "#64B5F6", "black"), # deeper pastel blue
    ]


    for title, desc, color, text_color in humidity_levels:
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

with st.expander("Show Wind Speed Guide"):

    wind_levels = [
        ("Calm (0–2 km/h)", "Sea like a mirror — Smoke rises vertically", "#E8F5E9", "black"),
        ("Light Air (2–5 km/h)", "Ripples with no foam crests — Smoke drifts", "#C5E1A5", "black"),
        ("Light Breeze (6–11 km/h)", "Small wavelets — Leaves rustle", "#FFF59D", "black"),
        ("Gentle Breeze (12–19 km/h)", "Large wavelets — Leaves and twigs in motion", "#FFE082", "black"),
        ("Moderate Breeze (20–28 km/h)", "Small waves — Dust and loose paper blow", "#FFCC80", "black"),
        ("Fresh Breeze (29–38 km/h)", "Moderate waves — Small trees sway", "#FFAB91", "black"),
        ("Strong Breeze (39–50 km/h)", "Large waves — Large branches move", "#EF9A9A", "black"),
    ]
    for title, desc, color, text_color in wind_levels:
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

with st.expander("Show Rainfall Guide"):

    rain_levels = [
        ("No Rain (0 mm/hr)", "Dry conditions — no precipitation", "#E3F2FD", "black"), 
        ("Light Rain (0.1–2 mm/hr)", "Drizzle — light jacket enough", "#BBDEFB", "black"),
        ("Moderate Rain (2–7 mm/hr)", "Steady rain — umbrella recommended", "#90CAF9", "black"),
        ("Heavy Rain (7–15 mm/hr)", "Soaking rain — reduced visibility", "#64B5F6", "black"), 
        ("Very Heavy Rain (15–30 mm/hr)", "Intense rain — difficult travel", "#42A5F5", "white"), 
        ("Extreme Rain (30+ mm/hr)", "Downpour — flooding possible", "#2196F3", "white"),
    ]


    for title, desc, color, text_color in rain_levels:
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

with st.expander("Show Cloud Cover Guide"):

    cloud_levels = [
        ("Clear Sky (0–1 OKTA)", "Blue sky — no significant clouds", "#F5F5F5", "black"),
        ("Few Clouds (1–3 OKTA)", "Mostly sunny — small patches of cloud", "#E0E0E0", "black"),
        ("Scattered Clouds (3–5 OKTA)", "Mix of sun and cloud", "#BDBDBD", "black"),
        ("Broken Clouds (5–7 OKTA)", "Mostly cloudy — sun appears occasionally", "#9E9E9E", "white"),
        ("Overcast (8 OKTA)", "Fully covered sky — no direct sunlight", "#616161", "white"),
    ]

    for title, desc, color, text_color in cloud_levels:
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


#**************************************************************************************
# CODE FROM ORIGINAL COMFORT COMPASS APP

# 3. Select travel mode
# travel_mode = st.radio("How will you travel?:",["Car", "Plane"])
travel_mode = st.pills(
    "How will you travel?",
    options=["Car", "Plane"],
    default="Car",
    key="travel_mode"
)


# travel_time = st.number_input(
#     "Maximum travel time (hours)",
#     min_value=1,
#     max_value=12,
#     value=5,
#     step=1
# )

travel_time_options = [f"{i}hr" for i in range(1, 13)]

selected_travel_time = st.pills(
    "Maximum travel time",
    options=travel_time_options,
    default="5hr",
    key="travel_time"
)

# Convert "5h" → 5
travel_time = int(selected_travel_time.replace("hr", ""))





# 4. Select travel month
# Set travel related variables
# DROP DOWN MONTH 
# months = list(calendar.month_name)[1:]
# selected_month = st.selectbox("What month do you plan to travel?", months)
# *****************
# import calendar
# import datetime

months_short = [calendar.month_abbr[i] for i in range(1, 13)]

selected_month = st.pills(
    "What month do you plan to travel?:",
    options=months_short,
    default="Jan",
    key="travel_month_short"
)

current_year = datetime.datetime.now().year

# Convert short month name → month number
travel_month = months_short.index(selected_month) + 1


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
        
# Add new columns 
sampled_routes_df["Distance"] = sampled_routes_df["Distance"].round(0).astype(int).astype(str) + " km"

sampled_routes_df["temp_overall_min"] = temp_overall_min
sampled_routes_df["temp_overall_max"] = temp_overall_max

sampled_routes_df["uv_overall_min"] = uv_overall_min
sampled_routes_df["uv_overall_max"] = uv_overall_max

sampled_routes_df["humidity_overall_min"] = humidity_overall_min
sampled_routes_df["humidity_overall_max"] = humidity_overall_max

sampled_routes_df["wind_overall_min"] = wind_overall_min
sampled_routes_df["wind_overall_max"] = wind_overall_max

sampled_routes_df["rain_overall_min"] = rain_overall_min
sampled_routes_df["rain_overall_max"] = rain_overall_max

sampled_routes_df["cloud_overall_min"] = cloud_overall_min
sampled_routes_df["cloud_overall_max"] = cloud_overall_max

sampled_routes_df["travel_month"] = travel_month
sampled_routes_df["current_year"] = current_year

st.dataframe(sampled_routes_df)


#*****************************
# AIR POLLUTION CODE
#*****************************
# Updte with API data
# Test code for output with air polution
# sampled_routes_df["Comfort Score"] = 57
# sampled_routes_df["Air Pollution"] = "Good"

# cols_to_show = ["Comfort Score", "City", "Country", "Distance", "Air Pollution"]
# existing_cols = [c for c in cols_to_show if c in sampled_routes_df.columns]
# df_show = sampled_routes_df[existing_cols].copy()

# pollution_colors = {
#     "Good": "#3CB371",
#     "Moderate": "#FFD700",
#     "Unhealthy for Sensitive Groups": "#FFA500",
#     "Unhealthy": "#FF4500",
#     "Hazardous": "#800080"
# }

# html = """
# <style>
# table {
#     margin-left: auto;
#     margin-right: auto;
#     border-collapse: collapse;
# }
# th, td {
#     text-align: center;
#     padding: 6px 10px;
#     border-bottom: 1px solid #ddd;
# }
# </style>
# <table>
# <tr>
# """

# # headers
# for col in cols_to_show:
#     html += f"<th>{col}</th>"
# html += "</tr>"

# # rows
# for _, row in df_show.iterrows():
#     html += "<tr>"
#     for col in cols_to_show:
#         if col == "Air_Pollution":
#             color = pollution_colors.get(row[col], "white")
#             html += f'<td style="background-color:{color}; font-weight:600;">{row[col]}</td>'
#         else:
#             html += f"<td>{row[col]}</td>"
#     html += "</tr>"

# html += "</table>"

# st.markdown(html, unsafe_allow_html=True)
# ABOVE >> Test table

# Get temperature data -OPEN METEO nolonger working
# import time
# import requests

# sampled_routes_df["Temperature"] = float("nan")

# # temp_value = float("nan")
# temp_value = 99

# url = "https://climate-api.open-meteo.com/v1/climate"

# with st.spinner("Fetching temperature data..."):
#     progress = st.progress(0)
#     status = st.empty()

#     total = len(sampled_routes_df)

#     for i, (idx, location) in enumerate(sampled_routes_df.iterrows()):
#         latitude = location.Latitude
#         longitude = location.Longitude

#         status.write(f"Processing {location.City} ({i+1}/{total})")

#         params = {
#             "latitude": latitude,
#             "longitude": longitude,
#             "daily": ["temperature_2m_mean"],
#             "start_date": "2025-07-15",
#             "end_date": "2025-07-15",
#             "timezone": "auto"
#         }

#         # Retry loop
#         for attempt in range(3):
#             try:
#                 r = requests.get(url, params=params, timeout=10)
#                 data = r.json()

#                 temp_value = data["daily"]["temperature_2m_mean"][0]
#                 break

#             except Exception:
#                 time.sleep(1)

#         sampled_routes_df.at[idx, "Temperature"] = temp_value

#         # Update progress bar
#         progress.progress((i+1) / total)
#         time.sleep(0.1)

# status.success("Temperature data loaded!")

# st.dataframe(
#     sampled_routes_df[["City", "Country", "Temperature"]]
# )

# WORKING TEMP API CODE - new meteostat code
# import streamlit as st
# from datetime import date
# import meteostat as ms

# # Add Temperature column
# sampled_routes_df["Temperature"] = float("nan")

# with st.spinner("Fetching temperature data..."):
#     progress = st.progress(0)
#     status = st.empty()

#     total = len(sampled_routes_df)

#     # Fixed date for your sampling
#     # start = datetime(2025, 7, 15)
#     # end = datetime(2025, 7, 15)

#     for i, (idx, location) in enumerate(sampled_routes_df.iterrows()):
#         lat = location.Latitude
#         lon = location.Longitude
#         POINT = ms.Point(lat, lon)

#         START = date(2025, 7, 15)
#         END = date(2025, 7, 15)

#         stations = ms.stations.nearby(POINT, limit=4)
#         ts = ms.daily(stations, START, END)
#         df = ms.interpolate(ts, POINT).fetch()


#         status.write(f"Getting temperature data for {location.City} ({i+1}/{total})")

#         # Extract tavg (mean temperature)
#         if not df.empty and "temp" in df.columns:
#             temp_value = df["temp"].iloc[0]
#         else:
#             temp_value = float("nan")

#         sampled_routes_df.at[idx, "Temperature"] = temp_value

#         progress.progress((i + 1) / total)
#         time.sleep(0.05)

# status.success("Temperature data loaded!")

# ****************************************
#METEO STAT CODE - used when other API stoped working
# ****************************************
# Extra Variables
# import streamlit as st
# from datetime import date
# import meteostat as ms
# import time

# # Add all new columns
# sampled_routes_df["Temperature"] = float("nan")
# sampled_routes_df["Wind_Speed"] = float("nan")
# sampled_routes_df["Humidity"] = float("nan")
# sampled_routes_df["Precipitation"] = float("nan")
# sampled_routes_df["Sunshine"] = float("nan")
# sampled_routes_df["Cloud_Cover"] = float("nan")

# with st.spinner("Fetching weather data..."):
#     progress = st.progress(0)
#     status = st.empty()

#     total = len(sampled_routes_df)

#     for i, (idx, location) in enumerate(sampled_routes_df.iterrows()):
#         lat = location.Latitude
#         lon = location.Longitude
#         POINT = ms.Point(lat, lon)

#         START = date(2025, 7, 15)
#         END = date(2025, 7, 15)

#         stations = ms.stations.nearby(POINT, limit=4)
#         ts = ms.daily(stations, START, END)
#         df = ms.interpolate(ts, POINT).fetch()

#         status.write(f"Getting weather data for {location.City} ({i+1}/{total})")

#         # Helper function
#         def get_value(df, col):
#             if not df.empty and col in df.columns:
#                 return df[col].iloc[0]
#             return float("nan")

#         # Extract variables
#         temp_value = get_value(df, "temp")
#         wspd_value = get_value(df, "wspd")
#         rhum_value = get_value(df, "rhum")
#         prcp_value = get_value(df, "prcp")
#         tsun_value = get_value(df, "tsun")
#         cldc_value = get_value(df, "cldc")

#         # Assign to dataframe
#         sampled_routes_df.at[idx, "Temperature"] = temp_value
#         sampled_routes_df.at[idx, "Wind Speed"] = wspd_value
#         sampled_routes_df.at[idx, "Humidity"] = rhum_value
#         sampled_routes_df.at[idx, "Precipitation"] = prcp_value
#         sampled_routes_df.at[idx, "Sunshine"] = tsun_value
#         sampled_routes_df.at[idx, "Cloud Cover"] = cldc_value

#         progress.progress((i + 1) / total)
#         time.sleep(0.05)

# status.success("Weather data loaded!")

# WORKING CODE FROM ALEX FOR OPEN METEO
# ***This is replaced by earlier code - check formating matches
# Turn airports.dat in dataframe airports_df

# **********************
# INITIAL DATFRAME
# **********************
# airports_df = pd.read_csv("airports.dat", header=None, index_col=0)
# airports_df.columns = ["Airport", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude", "Altitude", "Timezone", "DST", "TZ", "Type", "Source"]
# airports_df.index.name = 'AirportID'
# **********************
# INITIAL DATFRAME
# **********************
# >>> This can be replaced by earlier code - check formating matches - use ***sampled_routes_df***

# **********************
# KEY FUNCTION
# **********************
import requests
import pandas as pd
import time
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from dateutil.relativedelta import relativedelta

session = requests.Session()

def get_weather_new(airport, lat, lon, start_date, end_date, max_retries=5):
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_mean",
            "cloud_cover_mean",
            "relative_humidity_2m_mean",
            "wind_speed_10m_mean",
            "rain_sum"
            # 'uv_index_max'
        ],
        "timezone": "auto",
    }

    response = None

    for attempt in range(max_retries):

        try:
            response = session.get(url, params=params, timeout=30)

            response.raise_for_status()

            data = response.json()

            df = pd.DataFrame(data["daily"])

            df["latitude"] = data["latitude"]
            df["longitude"] = data["longitude"]
            df["timezone"] = data["timezone"]
            df["Arrival_Airport"] = airport

            return df

        except requests.exceptions.HTTPError as e:

            if response.status_code < 500 and response.status_code != 429:
                print(f"[CLIENT ERROR] {airport}: {response.status_code}")
                print(response.text)
                return None


        except requests.exceptions.RequestException as e:
            print(f"[{airport}] Request failed: {e}")

        wait = 2 ** (attempt + 3)
        time.sleep(wait)

    print(f"[FAILED] {airport}")

    return None


def get_airports_weather(sampled_routes_df):
    MAX_WORKERS = 10
    weather_dataframes = []
    futures = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        for row in sampled_routes_df.itertuples(index=False):
                airport = row.Arrival_Airport

                # Define the date
                year = row.current_year - 1
                month = int(row.travel_month)
                day = 15
                start_date = f"{year}-{month:02d}-{day:02d}"
                end_date = start_date

                futures.append(
                    executor.submit(
                        get_weather_new,
                        airport,
                        row.Latitude,
                        row.Longitude,
                        start_date,
                        end_date
                    )
                )
    
        for future in as_completed(futures):
            try:
                df = future.result(timeout=5)
                if df is not None:
                    weather_dataframes.append(df)
    
            except Exception as e:
                print(f"[ERROR] {e}")
    
    return weather_dataframes

# **********************
# KEY FUNCTION
# **********************



# **********************
# FILES AND DATAFRAMES - IS THIS USED?
# **********************
import os
def dump_complete_to_a_files(df_list):
    complete_airports = list(
        {
            airport
            for df in df_list
            for airport in df["Airport"]
        }
    )
    
    with open(f'complete_airports_sample.txt', "a", encoding="utf-8") as file:
        for airport in complete_airports:
            file.write(f"{airport}\n")

    combined_df = pd.concat(df_list, axis=0, ignore_index=True)
    file_exists = os.path.exists(f'airport_weather_combined_sample.csv')
    combined_df.to_csv(f'airport_weather_combined_sample.csv', mode="a", index=False, header=not file_exists)

# **********************
# FILES AND DATAFRAMES
# **********************

# **********************
# PICK 10 THEN RUN CALL WITH DATES
# **********************

sampled_routes_df = sampled_routes_df.reset_index(drop=True)
random_ten_weather = get_airports_weather(sampled_routes_df)
random_ten_weather = pd.concat(random_ten_weather, ignore_index=True)

weather_results_df = sampled_routes_df.merge(
    random_ten_weather,
    on="Arrival_Airport",
    how="left"
)


# TEMP RESULTS FOR DEBUGING
st.dataframe(
    weather_results_df[[
        "City", 
        "Country", 
        "temperature_2m_mean",
        "cloud_cover_mean",
        "relative_humidity_2m_mean",
        "wind_speed_10m_mean",
        "rain_sum"
        ]]
)

# ****************************************
# UV data API when meteo stop working
# ****************************************
# import requests
# import pandas as pd

sampled_routes_df["UV"] = float("nan")

def get_uv(lat, lon):
    url = f"https://currentuvindex.com/api/v1/uvi?latitude={lat}&longitude={lon}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        uv_values = []

        # 1. Add all UV values from the past 24 hours (history)
        history = data.get("history", [])
        df_h = pd.DataFrame(history)

        if not df_h.empty:
            uv_values.extend(df_h["uvi"].astype(float).tolist())

        # 2. Add all UV values from forecast (today + next 2 days)
        forecast = data.get("forecast", [])
        df_f = pd.DataFrame(forecast)

        if not df_f.empty:
            uv_values.extend(df_f["uvi"].astype(float).tolist())

        # 3. Add current UV as fallback
        if "now" in data and "uvi" in data["now"]:
            uv_values.append(float(data["now"]["uvi"]))

        # 4. Return the maximum UV value found
        if uv_values:
            return max(uv_values)

        return float("nan")

    except:
        return float("nan")



with st.spinner("Fetching UV data..."):
    progress = st.progress(0)
    status = st.empty()

    total = len(sampled_routes_df)

    for i, (idx, location) in enumerate(sampled_routes_df.iterrows()):
        lat = location.Latitude
        lon = location.Longitude

        status.write(f"Getting UV data for {location.City} ({i+1}/{total})")

        uv_value = get_uv(lat, lon)

        sampled_routes_df.at[idx, "UV"] = uv_value

        progress.progress((i + 1) / total)
        time.sleep(0.05)

status.success("UV data loaded!")

# HIDE UV RESULT TABLE
# st.dataframe(
#     sampled_routes_df[["City", "Country", "Temperature", "UV"]]
# )





# Calculate the Comfort Score

def temp_distance(temp):
    if temp < Temp_lo:
        return Temp_lo - temp
    elif temp > Temp_hi:
        return temp - Temp_hi
    else:
        return 0

def uv_distance(uv):
    if uv > UV_hi:
        return uv - UV_hi
    else:
        return 0

# Comfort score model
def calculate_comfort_score(temp_distance, uv_distance):
    # UV of 11 = 5
    # intercept = 96.2684
    # coeff_Temp_Distance = 0.7319
    # coeff_Temp_DistanceSqd = -0.3554
    # coeff_UV_Distance = -6.0585
    # coeff_UV_DistanceSqd = -0.1929

    # UV 11 = 50
    intercept = 96.2684
    coeff_Temp_Distance = 0.7319
    coeff_Temp_DistanceSqd = -0.3554
    coeff_UV_Distance = -6.0585
    coeff_UV_DistanceSqd = -0.1929

    return (
        intercept
        + coeff_Temp_Distance * temp_distance
        + coeff_Temp_DistanceSqd * (temp_distance ** 2)
        + coeff_UV_Distance * uv_distance
        + coeff_UV_DistanceSqd * (uv_distance ** 2)
    )

# Distance columns
sampled_routes_df["Temp_Distance"] = sampled_routes_df["Temperature"].apply(temp_distance)
sampled_routes_df["UV_Distance"] = sampled_routes_df["UV"].apply(uv_distance)

# Comfort score (correct column name)
sampled_routes_df["Comfort Score"] = sampled_routes_df.apply(
    lambda row: calculate_comfort_score(row["Temp_Distance"], row["UV_Distance"]),
    axis=1
)

# Sort
# sorted_df = sampled_routes_df.sort_values(
#     by="Comfort_Score",
#     ascending=False
# ).reset_index(drop=True)

# # Format numbers BEFORE styling
# sorted_df["Comfort_Score"] = sorted_df["Comfort_Score"].round(0).astype(int)
# sorted_df["Temperature"] = sorted_df["Temperature"].map(lambda x: f"{x:.1f}")
# sorted_df["UV"] = sorted_df["UV"].map(lambda x: f"{x:.1f}")
# sorted_df["Temp_Distance"] = sorted_df["Temp_Distance"].map(lambda x: f"{x:.1f}")
# sorted_df["UV_Distance"] = sorted_df["UV_Distance"].map(lambda x: f"{x:.1f}")

# # Select columns
# display_df = sorted_df[
#     [
#         "Comfort_Score",
#         "City",
#         "Country",
#         "Temperature",
#         "UV"
#     ]
# ]

# # Centre table
# styled_df = (
#     display_df.style
#     .set_properties(**{"text-align": "center"})
#     .set_table_styles([dict(selector="th", props=[("text-align", "center")])])
# )

# # Display with alignment working
# st.write(styled_df)



# Build formatted DataFrame first
sorted_df = sampled_routes_df.sort_values(
    by="Comfort Score",
    ascending=False
).reset_index(drop=True)

sorted_df["Comfort Score"] = sorted_df["Comfort Score"].round(0).astype(int)
sorted_df["Temperature"] = sorted_df["Temperature"].map(lambda x: f"{x:.1f}")
sorted_df["UV"] = sorted_df["UV"].map(lambda x: f"{x:.1f}")

# Select columns
display_df = sorted_df[
    [
        "Comfort Score",
        "City",
        "Country",
        "Temperature",
        "UV"
    ]
]

# Build HTML table
html = """
<style>
table {
    margin-left: auto;
    margin-right: auto;
    border-collapse: collapse;
    font-size: 15px;
}
th, td {
    text-align: center;
    padding: 6px 12px;
    border-bottom: 1px solid #ddd;
}
td.left {
    text-align: left;
}
th {
    font-weight: bold;
}
</style>
<table>
<tr>
"""

# Add headers
for col in display_df.columns:
    html += f"<th>{col}</th>"
html += "</tr>"

# Add rows
for _, row in display_df.iterrows():
    html += "<tr>"
    for col in display_df.columns:
        # Left-align City and Country
        if col in ["City", "Country"]:
            html += f"<td class='left'>{row[col]}</td>"
        else:
            html += f"<td>{row[col]}</td>"
    html += "</tr>"

html += "</table>"

st.markdown(html, unsafe_allow_html=True)

