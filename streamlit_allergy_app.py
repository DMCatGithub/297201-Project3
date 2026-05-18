import pandas as pd
import streamlit as st
import calendar
import datetime
from math import radians, sin, cos, sqrt, atan2

import openmeteo_requests

import requests_cache
from retry_requests import retry


st.title("Allergy‑Aware Holiday Planner")

# LOAD AIRPORTS: Turn airports.dat in dataframe airports_df
airports_df = pd.read_csv("airports.dat", header=None)
airports_df.columns = ["AirportID", "Airport", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude", "Altitude", "Timezone", "DST", "TZ", "Type", "Source"]

# Removeing duplicate cities in same country (Only want city to show once in selection)
airports_unique_cities_df = airports_df.drop_duplicates(subset=["Country", "City"])

# LOAD ROUTES: Turn routes.dat into dataframe routes_df
routes_df = pd.read_csv("routes.dat", header=None)
routes_df.columns = ["Airline", "AirlineID", "Departure_Airport", "Departure_AirportID", "Arrival_Airport", "Arrival_AirportID", "Codeshare", "Stops", "Equipment"]

# Selections from user - thru streamlit
# 
# -----------------------------------------

allergy_options = [
    "Allergy type1",
    "Allergy type2",
    "Allergy type3",
    "Allergy type4",
    "Allergy type5"
]

selected_allergies = st.multiselect(
    "Select all allergy types that apply:",
    options=allergy_options,
    default=["Allergy type1","Allergy type2","Allergy type3","Allergy type4","Allergy type5"])


Temp_lo, Temp_hi = st.slider(
    "Select preferred temperature range (°C)",
    min_value=-10,
    max_value=50,
    value=(18, 25)   # default min/max
)

travel_mode = st.radio("How will you travel?",["Car", "Plane"])

travel_time = st.number_input(
    "Maximum travel time (hours)",
    min_value=1,
    max_value=12,
    value=5,
    step=1
)

current_year = datetime.datetime.now().year

months = list(calendar.month_name)[1:]
selected_month = st.selectbox("What month do you plan to travel?", months)

travel_month = months.index(selected_month) + 1

AVG_CAR_SPEED = 80  # km/h
AVG_PLANE_SPEED = 800  # km/h

if travel_mode == "Car":
    travel_distance = travel_time * AVG_CAR_SPEED
else:
    travel_distance = travel_time * AVG_PLANE_SPEED


# Temp_hi = 25
# Temp_lo = 18

Humidity_hi = 75    # Based on the catagory selected by user
Humidity_lo = 40

# Convert selected allergies into fixed slots
Allergy_1 = selected_allergies[0] if len(selected_allergies) > 0 else None
Allergy_2 = selected_allergies[1] if len(selected_allergies) > 1 else None
Allergy_3 = selected_allergies[2] if len(selected_allergies) > 2 else None
Allergy_4 = selected_allergies[3] if len(selected_allergies) > 3 else None
Allergy_5 = selected_allergies[4] if len(selected_allergies) > 4 else None

# -----------------------------------------

# Departure_Country = "United Kingdom"
# Departure_City = "London"
# Departure_Airports_df = airports_df.loc[(airports_df["City"] == Departure_City) & (airports_df["Country"] == Departure_Country), "IATA"]


unique_countries = sorted(airports_unique_cities_df["Country"].dropna().unique())
Departure_Country = st.selectbox("Select your country",options=unique_countries)

if not Departure_Country:
    st.stop()


towns_in_selected_country = sorted(airports_unique_cities_df.loc[airports_unique_cities_df["Country"] == Departure_Country, "City"].dropna().unique())
Departure_City = st.selectbox("Select nearest town or city",options=towns_in_selected_country)

if not Departure_City:
    st.stop()

# --- AIRPORT SELECTION LOGIC ---

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

  


# Function for working out distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radius in km
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c






def plane_destinations ():
# Make dataframe of all "routes_from_df" "Departure_Airport"
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

        routes_from_df.at[idx,"Humidity_hi"] = Humidity_hi
        routes_from_df.at[idx,"Humidity_lo"] = Humidity_lo

        routes_from_df.at[idx,"Allergy_1"] = Allergy_1
        routes_from_df.at[idx,"Allergy_2"] = Allergy_2
        routes_from_df.at[idx,"Allergy_3"] = Allergy_3
        routes_from_df.at[idx,"Allergy_4"] = Allergy_4
        routes_from_df.at[idx,"Allergy_5"] = Allergy_5

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


sampled_routes_df = plane_destinations()

allergy_slots = selected_allergies + [None] * (5 - len(selected_allergies))
Allergy_1, Allergy_2, Allergy_3, Allergy_4, Allergy_5 = allergy_slots[:5]

sampled_routes_df["Allergy_1"] = Allergy_1
sampled_routes_df["Allergy_2"] = Allergy_2
sampled_routes_df["Allergy_3"] = Allergy_3
sampled_routes_df["Allergy_4"] = Allergy_4
sampled_routes_df["Allergy_5"] = Allergy_5

sampled_routes_df["Temp_hi"] = Temp_hi
sampled_routes_df["Temp_lo"] = Temp_lo

# st.table(routes_from_df)
# sampled_routes_df = sampled_routes_df[[["City", "Country", "Distance", "Temp_hi", "Temp_lo", "Allergy_1", "Allergy_2", "Allergy_3", "Allergy_4", "Allergy_5"]]
st.dataframe(sampled_routes_df[["City", "Country", "Distance", "Temp_hi", "Temp_lo", "Allergy_1", "Allergy_2", "Allergy_3", "Allergy_4", "Allergy_5"]], hide_index=True)

# *************************

# Modified previous weather API to work with output from above
# Update to get weather data from the 1-28 of the travel_month selected by user - from previous year (add another for loop for additional years)
# Not linked to streamlit so example variables are coded in.


#Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

weather_data = []

# Potentially create start date and end date in streamlite
# Travel_month = 8
# Current_year = 2026

First_day = 1
Last_day = 28

for idx, row in sampled_routes_df.iterrows():

    latitude = row["Latitude"]
    longitude = row["Longitude"]
    city = row["City"]
    country = row["Country"]

    start_date = datetime.date(int(current_year - 1), int(travel_month), int(First_day))
    end_date = datetime.date(int(current_year - 1), int(travel_month), int(Last_day))

    #Make sure all required weather variables are listed here
    #The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_mean", "apparent_temperature_mean", "cloud_cover_mean", "dew_point_2m_mean", "relative_humidity_2m_mean", "surface_pressure_mean", "wind_gusts_10m_mean", "wind_speed_10m_mean", "wet_bulb_temperature_2m_mean", "pressure_msl_mean"],
        "timezone": "auto",
    }
    responses = openmeteo.weather_api(url, params = params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()

    # One day only
    # weather_data.append({
    #     "Start_Date": start_date.strftime("%Y-%m-%d"),
    #     "City" : city,
    #     "Country" : country,
    #     "Latitude": latitude,
    #     "Longitude": longitude,
    #     "Temperature": daily.Variables(0).ValuesAsNumpy()[0],
    #     "Apparent_Temp": daily.Variables(1).ValuesAsNumpy()[0],
    #     "Cloud_Cover": daily.Variables(2).ValuesAsNumpy()[0],
    #     "Dew_Point": daily.Variables(3).ValuesAsNumpy()[0],
    #     "Humidity": daily.Variables(4).ValuesAsNumpy()[0],
    #     "Surface_Pressure": daily.Variables(5).ValuesAsNumpy()[0],
    #     "Wind_Gusts": daily.Variables(6).ValuesAsNumpy()[0],
    #     "Wind_Speed": daily.Variables(7).ValuesAsNumpy()[0],
    #     "Wet_Bulb": daily.Variables(8).ValuesAsNumpy()[0],
    #     "Pressure": daily.Variables(9).ValuesAsNumpy()[0],
    # })

    # 28 days works for all months and enough data for a month
    for i in range(28):
        date_i = start_date + datetime.timedelta(days=i)

        weather_data.append({
            "Date": date_i.strftime("%Y-%m-%d"),
            "Year": date_i.strftime("%Y"),
            "City" : city,
            "Country" : country,
            "Latitude": latitude,
            "Longitude": longitude,
            "Temperature": daily.Variables(0).ValuesAsNumpy()[i],
            "Apparent_Temp": daily.Variables(1).ValuesAsNumpy()[i],
            "Cloud_Cover": daily.Variables(2).ValuesAsNumpy()[i],
            "Dew_Point": daily.Variables(3).ValuesAsNumpy()[i],
            "Humidity": daily.Variables(4).ValuesAsNumpy()[i],
            "Surface_Pressure": daily.Variables(5).ValuesAsNumpy()[i],
            "Wind_Gusts": daily.Variables(6).ValuesAsNumpy()[i],
            "Wind_Speed": daily.Variables(7).ValuesAsNumpy()[i],
            "Wet_Bulb": daily.Variables(8).ValuesAsNumpy()[i],
            "Pressure": daily.Variables(9).ValuesAsNumpy()[i],
    })


weather_data_df = pd.DataFrame(weather_data)
weather_data_df.head(50)


