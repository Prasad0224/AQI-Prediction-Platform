from flask import Flask, jsonify
from flask_cors import CORS
import requests
import pandas as pd
import joblib

app = Flask(__name__)
CORS(app) 

# Load trained model
model = joblib.load("../../models/aqi_model.pkl")

# Government API details
API_KEY = "579b464db66ec23bdd000001ba7c83c075784fde7ead526137a405e4"
AQI_URL = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"

# City coordinates for weather
CITY_COORDS = {
    "Delhi": (28.61, 77.20),
    "Mumbai": (19.07, 72.87),
    "Pune": (18.52, 73.85),
    "Bengaluru": (12.97, 77.59),
    "Chennai": (13.08, 80.27)
}

@app.route("/predict/<city>")
def predict(city):

    # --- Fetch live pollutant data ---
    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[city]": city,
        "limit": 100
    }

    response = requests.get(AQI_URL, params=params)
    data = response.json()["records"]

    df = pd.DataFrame(data)[["pollutant_id", "avg_value"]]

    df["avg_value"] = pd.to_numeric(df["avg_value"], errors="coerce")


    pivot = df.pivot_table(values="avg_value", columns="pollutant_id", aggfunc="first")

    pivot = pivot.fillna(0)


    # Clean column names
    pivot.columns = [c.lower().replace('.', '') for c in pivot.columns]
    pivot = pivot.rename(columns={"pm25":"PM2.5", "pm10":"PM10",
                                   "no2":"NO2", "so2":"SO2",
                                   "co":"CO", "ozone":"O3",
                                   "nh3":"NH3"})
    
    
    pivot = pivot[["PM2.5", "PM10", "NO2", "SO2", "CO", "O3", "NH3"]]


    # --- Fetch live weather ---
    lat, lon = CITY_COORDS[city]
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current="
        f"temperature_2m,relative_humidity_2m,wind_speed_10m"
    )

    weather_data = requests.get(weather_url).json()["current"]

    # Weather features
    # pivot["temperature"] = weather_data["temperature_2m"]
    # pivot["humidity"] = weather_data["relative_humidity_2m"]
    # pivot["wind_speed"] = weather_data["wind_speed_10m"]

    # --- Predict AQI ---
    prediction = model.predict(pivot)[0]

    return jsonify({
        "city": city,
        "predicted_AQI": round(float(prediction), 2)
    })


if __name__ == "__main__":
    app.run(debug=True)