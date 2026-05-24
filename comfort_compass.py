import pandas as pd
import streamlit as st
import calendar
import datetime
import time
from math import radians, sin, cos, sqrt, atan2

import openmeteo_requests

import requests_cache
from retry_requests import retry


st.title("Comfort Compass")

# LOAD AIRPORTS: Turn airports.dat in dataframe airports_df
airports_df = pd.read_csv("airports.dat", header=None)
airports_df.columns = ["AirportID", "Airport", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude", "Altitude", "Timezone", "DST", "TZ", "Type", "Source"]

# Removeing duplicate cities in same country (Only want city to show once in selection)
airports_unique_cities_df = airports_df.drop_duplicates(subset=["Country", "City"])

# LOAD ROUTES: Turn routes.dat into dataframe routes_df
routes_df = pd.read_csv("routes.dat", header=None)
routes_df.columns = ["Airline", "AirlineID", "Departure_Airport", "Departure_AirportID", "Arrival_Airport", "Arrival_AirportID", "Codeshare", "Stops", "Equipment"]

# Selections from user - thru streamlit

# UV Colour chart with more info
# st.markdown("#### UV Index Guide")

# uv_levels = [
#     ("Low (1–2)", "Burn ~60 min — Minimal protection", "#3CB371", "white"),
#     ("Moderate (3–5)", "Burn ~40 min — Protection recommended", "#FFD700", "black"),
#     ("High (6–7)", "Burn ~30 min — Protection essential", "#FF8C00", "white"),
#     ("Very High (8–10)", "Burn ~20 min — Extra protection needed", "#FF4500", "white"),
#     ("Extreme (11+)", "Burn <15 min — Avoid sun exposure", "#9400D3", "white"),
# ]

# for title, desc, color, text_color in uv_levels:
#     st.markdown(
#         f"""
#         <div style="
#             background-color:{color};
#             padding:8px 12px;
#             border-radius:6px;
#             margin-bottom:6px;
#             color:{text_color};
#             font-weight:600;
#             font-size:14px;">
#             {title} — {desc}
#         </div>
#         """,
#         unsafe_allow_html=True
#     )


# 1. Set UV Slider
UV_lo = 1   # fixed
UV_hi = st.slider(
    "Select preferred maximum UV index (see UV index guide below):",
    min_value = 1,
    max_value = 11,
    value = 3, # default value
    step = 1
)


with st.expander("Show UV Index Guide"):

    uv_levels = [
        ("Low (1–2)", "Burn ~60 min — Minimal protection", "#3CB371", "black"),
        ("Moderate (3–5)", "Burn ~40 min — Protection recommended", "#FFD700", "black"),
        ("High (6–7)", "Burn ~30 min — Protection essential", "#FF8C00", "black"),
        ("Very High (8–10)", "Burn ~20 min — Extra protection needed", "#FF4500", "black"),
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

# 2. Set Temperature slider
Temp_lo, Temp_hi = st.slider(
    "Select preferred temperature range (°C):",
    min_value = -10,
    max_value = 50,
    value=(21, 25)   # default min/max
)

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

# Extra Variables
import streamlit as st
from datetime import date
import meteostat as ms
import time

# Add all new columns
sampled_routes_df["Temperature"] = float("nan")
sampled_routes_df["Wind_Speed"] = float("nan")
sampled_routes_df["Humidity"] = float("nan")
sampled_routes_df["Precipitation"] = float("nan")
sampled_routes_df["Sunshine"] = float("nan")
sampled_routes_df["Cloud_Cover"] = float("nan")

with st.spinner("Fetching weather data..."):
    progress = st.progress(0)
    status = st.empty()

    total = len(sampled_routes_df)

    for i, (idx, location) in enumerate(sampled_routes_df.iterrows()):
        lat = location.Latitude
        lon = location.Longitude
        POINT = ms.Point(lat, lon)

        START = date(2025, 7, 15)
        END = date(2025, 7, 15)

        stations = ms.stations.nearby(POINT, limit=4)
        ts = ms.daily(stations, START, END)
        df = ms.interpolate(ts, POINT).fetch()

        status.write(f"Getting weather data for {location.City} ({i+1}/{total})")

        # Helper function
        def get_value(df, col):
            if not df.empty and col in df.columns:
                return df[col].iloc[0]
            return float("nan")

        # Extract variables
        temp_value = get_value(df, "temp")
        wspd_value = get_value(df, "wspd")
        rhum_value = get_value(df, "rhum")
        prcp_value = get_value(df, "prcp")
        tsun_value = get_value(df, "tsun")
        cldc_value = get_value(df, "cldc")

        # Assign to dataframe
        sampled_routes_df.at[idx, "Temperature"] = temp_value
        sampled_routes_df.at[idx, "Wind_Speed"] = wspd_value
        sampled_routes_df.at[idx, "Humidity"] = rhum_value
        sampled_routes_df.at[idx, "Precipitation"] = prcp_value
        sampled_routes_df.at[idx, "Sunshine"] = tsun_value
        sampled_routes_df.at[idx, "Cloud_Cover"] = cldc_value

        progress.progress((i + 1) / total)
        time.sleep(0.05)

status.success("Weather data loaded!")



# HIDE TEMP RESULT TABLE
st.dataframe(
    sampled_routes_df[["City", "Country", "Temperature", "Wind_Speed","Humidity","Precipitation","Sunshine","Cloud_Cover"]]
)

# UV data
import requests
import pandas as pd

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

