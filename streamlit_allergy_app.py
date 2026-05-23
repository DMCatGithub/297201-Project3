import pandas as pd
import streamlit as st
import calendar
import datetime
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
st.markdown("#### UV Index Guide")

uv_levels = [
    ("Low (1–2)", "Burn ~60 min — Minimal protection", "#3CB371", "white"),
    ("Moderate (3–5)", "Burn ~40 min — Protection recommended", "#FFD700", "black"),
    ("High (6–7)", "Burn ~30 min — Protection essential", "#FF8C00", "white"),
    ("Very High (8–10)", "Burn ~20 min — Extra protection needed", "#FF4500", "white"),
    ("Extreme (11+)", "Burn <15 min — Avoid sun exposure", "#9400D3", "white"),
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



# 1. Set UV Slider
UV_lo = 1   # fixed
UV_hi = st.slider(
    "Select preferred maximum UV index (see UV index guide below):",
    min_value = 1,
    max_value = 11,
    value = 5, # default value
    step = 1
)

# 2. Set Temperature slider
Temp_lo, Temp_hi = st.slider(
    "Select preferred temperature range (°C):",
    min_value = -10,
    max_value = 50,
    value=(18, 25)   # default min/max
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
sampled_routes_df["Comfort Score"] = 57
sampled_routes_df["Air Pollution"] = "Good"

cols_to_show = ["Comfort Score", "City", "Country", "Distance", "Air Pollution"]
existing_cols = [c for c in cols_to_show if c in sampled_routes_df.columns]
df_show = sampled_routes_df[existing_cols].copy()

pollution_colors = {
    "Good": "#3CB371",
    "Moderate": "#FFD700",
    "Unhealthy for Sensitive Groups": "#FFA500",
    "Unhealthy": "#FF4500",
    "Hazardous": "#800080"
}

html = """
<style>
table {
    margin-left: auto;
    margin-right: auto;
    border-collapse: collapse;
}
th, td {
    text-align: center;
    padding: 6px 10px;
    border-bottom: 1px solid #ddd;
}
</style>
<table>
<tr>
"""

# headers
for col in cols_to_show:
    html += f"<th>{col}</th>"
html += "</tr>"

# rows
for _, row in df_show.iterrows():
    html += "<tr>"
    for col in cols_to_show:
        if col == "Air_Pollution":
            color = pollution_colors.get(row[col], "white")
            html += f'<td style="background-color:{color}; font-weight:600;">{row[col]}</td>'
        else:
            html += f"<td>{row[col]}</td>"
    html += "</tr>"

html += "</table>"

st.markdown(html, unsafe_allow_html=True)

# Get temperature data
# --- TEMPERATURE FETCH WITH PROGRESS BAR ---

# Fast Open-Meteo client
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

sampled_routes_df["Temperature"] = float("nan")

with st.spinner("Fetching temperature data..."):
    progress = st.progress(0)
    status = st.empty()

    total = len(sampled_routes_df)

    for i, (idx, row) in enumerate(sampled_routes_df.iterrows()):

        status.write(f"Processing {row['City']} ({i+1}/{total})")

        params = {
            "latitude": row["Latitude"],
            "longitude": row["Longitude"],
            "start_date": "2025-07-15",
            "end_date": "2025-07-15",
            "daily": ["temperature_2m_mean"],
            "timezone": "auto"
        }

        # FAST binary API call
        responses = openmeteo.weather_api(
            "https://archive-api.open-meteo.com/v1/archive",
            params=params
        )

        response = responses[0]
        daily = response.Daily()

        # Extract temperature
        temp_value = daily.Variables(0).ValuesAsNumpy()[0]

        sampled_routes_df.at[idx, "Temperature"] = temp_value

        # Update progress bar
        progress.progress((i+1) / total)

        # Small delay so UI visibly updates
        time.sleep(0.1)

status.success("Temperature data loaded")


