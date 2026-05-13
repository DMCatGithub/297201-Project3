import pandas as pd
import streamlit as st
import calendar
import datetime

# Turn airports.dat in dataframe airports_df
airports_df = pd.read_csv("airports.dat", header=None)
airports_df.columns = ["AirportID", "Airport", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude", "Altitude", "Timezone", "DST", "TZ", "Type", "Source"]

# Turn routes.dat into dataframe routes_df
routes_df = pd.read_csv("routes.dat", header=None)
routes_df.columns = ["Airline", "AirlineID", "Departure_Airport", "Departure_AirportID", "Arrival_Airport", "Arrival_AirportID", "Codeshare", "Stops", "Equipment"]

# Selections from user - thru streamlit
# -----------------------------------------
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

travel_distance = travel_time * 800

Temp_hi = 25
Temp_lo = 18

Humidity_hi = 75    # Based on the catagory selected by user
Humidity_lo = 40

Allergy_1 = "Grass"
Allergy_2 = "AirPollution"
Allergy_3 = None
# -----------------------------------------


## Test destinations ##
# -----------------------------------------
# Departure_Airport = "AKL"
# Departure_Airport = "SYD"
# Departure_Airport = "LAX" #Los Angles
# Departure_Airport = "HKG" #Hong Kong
# Departure_Airport = "LHR"   #London
# Departure_Airport = "SIN" #Singapore
# Departure_Airport = "DXB" #Dubai
# Departure_Airport = "CDG" #Paris
# -----------------------------------------

unique_countries = sorted(airports_df["Country"].dropna().unique())

selected_country = st.selectbox("Select your country",options=unique_countries)

towns_in_selected_country = sorted(airports_df.loc[airports_df["Country"] == selected_country, "City"].dropna().unique())

selected_town = st.selectbox("Select nearest town or city",options=towns_in_selected_country)

airports_in_town = airports_df[(airports_df["Country"] == selected_country) & (airports_df["City"] == selected_town)]

if len(airports_in_town) == 1:
    selected_airport = airports_in_town.iloc[0]
else:
    airport_options = airports_in_town.apply(
        lambda row: f"{row['Airport']} ({row['IATA']})",
        axis=1
    )

    selected_option = st.selectbox(
        "Select your preferred airport",
        options=airport_options
    )

    selected_airport_row = airports_in_town.iloc[
        airport_options.tolist().index(selected_option)
    ]

departure_airport = selected_airport_row["IATA"]


# Function for working out distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radius in km
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

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

    routes_from_df.at[idx,"Travel_Month"] = Travel_month
    routes_from_df.at[idx,"Current_year"] = Current_year

    routes_from_df.at[idx,"Temp_hi"] = Temp_hi
    routes_from_df.at[idx,"Temp_lo"] = Temp_lo

    routes_from_df.at[idx,"Humidity_hi"] = Humidity_hi
    routes_from_df.at[idx,"Humidity_lo"] = Humidity_lo

    routes_from_df.at[idx,"Allergy_1"] = Allergy_1
    routes_from_df.at[idx,"Allergy_2"] = Allergy_2
    routes_from_df.at[idx,"Allergy_3"] = Allergy_3

routes_from_df = routes_from_df.sort_values("Distance")
# routes_from_df

# Only routes within user target
routes_for_user_df = (routes_from_df[routes_from_df["Distance"] < Travel_distance].sort_values("Distance").reset_index(drop=True))
# routes_for_user_df

# Sample 10 destinations from the list
# sampled_routes_df = routes_for_user_df.sample(n=10, random_state=42)
sampled_routes_df = routes_for_user_df.sample(n=10)
sampled_routes_df

# *************************

# Modified previous weather API to work with output from above
# Update to get weather data from the 1-28 of the travel_month selected by user - from previous year (add another for loop for additional years)
# Not linked to streamlit so example variables are coded in.

import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import datetime

#Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

weather_data = []

# Potentially create start date and end date in streamlite
Travel_month = 8
Current_year = 2026

First_day = 1
Last_day = 28

for idx, row in sampled_routes_df.iterrows():

    if idx % 1000 == 0:   #It was taking a long time so added this counter to see progress
        print(f"At {idx}")

    latitude = row["Latitude"]
    longitude = row["Longitude"]
    city = row["City"]
    country = row["Country"]

    start_date = datetime.date(int(Current_year - 1), int(Travel_month), int(First_day))
    end_date = datetime.date(int(Current_year - 1), int(Travel_month), int(Last_day))

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


